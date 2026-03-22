"""DataSUS downloader with local parquet cache.

Download strategy (tried in order):
1. Cache hit        → load parquet from disk, skip download.
2. HTTP mirror      → DigitalOcean CDN mirror of DataSUS FTP (fast, no auth).
3. Direct FTP       → ftp.datasus.gov.br with passive mode.
4. ManualUpload     → raise ManualUploadRequired so the UI shows a file uploader.

DBC decompression uses `datasus-dbc` (pure Python / pre-compiled wheel,
works on Windows without a C compiler).

Verified filename patterns (from FTP inspection):
  SIH       → SIHSUS/200801_/Dados/RD{state}{year2}{month2}.dbc  (monthly, concatenated)
  SIM       → SIM/CID10/DORES/DO{state}{year}.dbc                (annual per state)
  SINASC    → SINASC/1996_/Dados/DNRES/DN{state}{year}.dbc       (annual per state)
  SINAN_TB  → SINAN/DADOS/FINAIS/TUBEBR{year2}.dbc  (<=2019)
             | SINAN/DADOS/PRELIM/TUBEBR{year2}.dbc  (>=2020)
  SINAN_*   → SINAN/DADOS/FINAIS/{PAT}BR{year2}.dbc  (national, filtered by UF)
"""

from __future__ import annotations

import ftplib
import io
import tempfile
from pathlib import Path

import pandas as pd
import requests

# Usa /tmp no Streamlit Cloud (filesystem read-only fora de /tmp)
# e data/raw localmente para persistência entre sessões.
_local_dir = Path(__file__).parent.parent.parent / "data" / "raw"
_tmp_dir   = Path("/tmp/datasus_raw")
try:
    _local_dir.mkdir(parents=True, exist_ok=True)
    RAW_DIR = _local_dir
except (PermissionError, OSError):
    _tmp_dir.mkdir(parents=True, exist_ok=True)
    RAW_DIR = _tmp_dir

STATES = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
    "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
    "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]

FTP_HOST    = "ftp.datasus.gov.br"
HTTP_MIRROR = "https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com"

# Configuration per system.
# SIH is monthly (pattern includes {month2}); others are annual.
# national=True means one file for all Brazil, filter by UF after download.
FTP_CONFIG = {
    "SIH": {
        "ftp_path":  "/dissemin/publicos/SIHSUS/200801_/Dados/",
        "http_path": "SIHSUS/200801_/Dados/",
        "pattern":   "RD{state}{year2}{month2}.dbc",
        "monthly":   True,
    },
    "SIM": {
        "ftp_path":  "/dissemin/publicos/SIM/CID10/DORES/",
        "http_path": "SIM/CID10/DORES/",
        "pattern":   "DO{state}{year}.dbc",
        "monthly":   False,
    },
    "SINASC": {
        "ftp_path":  "/dissemin/publicos/SINASC/1996_/Dados/DNRES/",
        "http_path": "SINASC/1996_/Dados/DNRES/",
        "pattern":   "DN{state}{year}.dbc",
        "monthly":   False,
    },
    "SINAN_TB": {
        # Directory changes depending on year
        "ftp_path_finais": "/dissemin/publicos/SINAN/DADOS/FINAIS/",
        "ftp_path_prelim": "/dissemin/publicos/SINAN/DADOS/PRELIM/",
        "http_path_finais": "SINAN/DADOS/FINAIS/",
        "http_path_prelim": "SINAN/DADOS/PRELIM/",
        "pattern":   "TUBEBR{year2}.dbc",
        "monthly":   False,
        "national":  True,
        "uf_col":    "SG_UF_NOT",
    },
    "SINAN_DENG": {
        "ftp_paths":  ["/dissemin/publicos/SINAN/DADOS/FINAIS/", "/dissemin/publicos/SINAN/DADOS/PRELIM/"],
        "http_paths": ["SINAN/DADOS/FINAIS/", "SINAN/DADOS/PRELIM/"],
        "pattern":   "DENGBR{year2}.dbc",
        "monthly":   False,
        "national":  True,
        "uf_col":    "SG_UF_NOT",
    },
    "SINAN_HANS": {
        "ftp_paths":  ["/dissemin/publicos/SINAN/DADOS/FINAIS/", "/dissemin/publicos/SINAN/DADOS/PRELIM/"],
        "http_paths": ["SINAN/DADOS/FINAIS/", "SINAN/DADOS/PRELIM/"],
        "pattern":   "HANSBR{year2}.dbc",
        "monthly":   False,
        "national":  True,
        "uf_col":    "SG_UF_NOT",
    },
    "SINAN_CHIK": {
        "ftp_paths":  ["/dissemin/publicos/SINAN/DADOS/FINAIS/", "/dissemin/publicos/SINAN/DADOS/PRELIM/"],
        "http_paths": ["SINAN/DADOS/FINAIS/", "SINAN/DADOS/PRELIM/"],
        "pattern":   "CHIKBR{year2}.dbc",
        "monthly":   False,
        "national":  True,
        "uf_col":    "SG_UF_NOT",
    },
    "SINAN_VIOL": {
        "ftp_paths":  ["/dissemin/publicos/SINAN/DADOS/FINAIS/", "/dissemin/publicos/SINAN/DADOS/PRELIM/"],
        "http_paths": ["SINAN/DADOS/FINAIS/", "SINAN/DADOS/PRELIM/"],
        "pattern":   "VIOLBR{year2}.dbc",
        "monthly":   False,
        "national":  True,
        "uf_col":    "SG_UF_NOT",
    },
    "SINAN_IEXO": {
        "ftp_paths":  ["/dissemin/publicos/SINAN/DADOS/PRELIM/", "/dissemin/publicos/SINAN/DADOS/FINAIS/"],
        "http_paths": ["SINAN/DADOS/PRELIM/", "SINAN/DADOS/FINAIS/"],
        "pattern":   "IEXOBR{year2}.dbc",
        "monthly":   False,
        "national":  True,
        "uf_col":    "SG_UF_NOT",
    },
    "SINAN_AIDS": {
        "ftp_paths":  ["/dissemin/publicos/SINAN/DADOS/PRELIM/", "/dissemin/publicos/SINAN/DADOS/FINAIS/"],
        "http_paths": ["SINAN/DADOS/PRELIM/", "SINAN/DADOS/FINAIS/"],
        "pattern":   "AIDABR{year2}.dbc",
        "monthly":   False,
        "national":  True,
        "uf_col":    "SG_UF_NOT",
    },
    "SINAN_SIFA": {
        "ftp_paths":  ["/dissemin/publicos/SINAN/DADOS/PRELIM/", "/dissemin/publicos/SINAN/DADOS/FINAIS/"],
        "http_paths": ["SINAN/DADOS/PRELIM/", "SINAN/DADOS/FINAIS/"],
        "pattern":   "SIFABR{year2}.dbc",
        "monthly":   False,
        "national":  True,
        "uf_col":    "SG_UF_NOT",
    },
}

UF_CODE = {
    "RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15",
    "AP": "16", "TO": "17", "MA": "21", "PI": "22", "CE": "23",
    "RN": "24", "PB": "25", "PE": "26", "AL": "27", "SE": "28",
    "BA": "29", "MG": "31", "ES": "32", "RJ": "33", "SP": "35",
    "PR": "41", "SC": "42", "RS": "43", "MS": "50", "MT": "51",
    "GO": "52", "DF": "53",
}


class ManualUploadRequired(Exception):
    """Raised when automatic download failed — user must upload CSV manually."""
    def __init__(self, system: str, state: str, year: int, reason: str = ""):
        self.system = system
        self.state  = state
        self.year   = year
        self.reason = reason
        super().__init__(
            f"Nao foi possivel baixar {system} {state} {year} automaticamente. "
            "Faca o download manual no TABNET e faca upload do CSV na plataforma."
        )


# ── Cache ─────────────────────────────────────────────────────────────────────

def _cache_path(system: str, state: str, year: int) -> Path:
    return RAW_DIR / f"{system.lower()}_{state.upper()}_{year}.parquet"


def _save(df: pd.DataFrame, system: str, state: str, year: int) -> pd.DataFrame:
    df.to_parquet(_cache_path(system, state, year), index=False)
    return df


# ── Filename helpers ──────────────────────────────────────────────────────────

def _name_variants(name: str) -> list[str]:
    return list(dict.fromkeys([name, name.upper(), name.lower()]))


def _resolve_filename(cfg: dict, state: str, year: int, month: int | None = None) -> str:
    y2 = str(year)[-2:]
    m2 = f"{month:02d}" if month is not None else ""
    return (
        cfg["pattern"]
        .replace("{state}",  state.upper())
        .replace("{year}",   str(year))
        .replace("{year2}",  y2)
        .replace("{month2}", m2)
    )


def _sinan_tb_dirs(year: int) -> tuple[str, str]:
    """Return (ftp_dir, http_dir) for SINAN_TB depending on year."""
    cfg = FTP_CONFIG["SINAN_TB"]
    if year <= 2019:
        return cfg["ftp_path_finais"], cfg["http_path_finais"]
    return cfg["ftp_path_prelim"], cfg["http_path_prelim"]


def _filter_national(df: pd.DataFrame, cfg: dict, state: str) -> pd.DataFrame:
    """Filter national SINAN file to a single UF."""
    code = UF_CODE.get(state.upper(), "")
    if not code:
        return df
    uf_col_hint = cfg.get("uf_col")
    filter_col = None
    if uf_col_hint and uf_col_hint in df.columns:
        filter_col = uf_col_hint
    else:
        for col in df.columns:
            if "SG_UF" in col.upper():
                filter_col = col
                break
    if filter_col:
        df = df[df[filter_col].astype(str).str.strip() == str(int(code))]
    return df


# ── DBC → DataFrame ──────────────────────────────────────────────────────────

def _dbc_to_df(dbc_bytes: bytes, max_rows: int | None = None) -> pd.DataFrame:
    """Decompress DBC bytes → DataFrame via datasus-dbc + dbfread.

    max_rows: if set, stop reading after this many records (prevents OOM for
    large files like SIH SP which can exceed 1 GB when fully loaded).
    """
    from datasus_dbc import decompress_bytes
    import dbfread

    dbf_bytes = decompress_bytes(dbc_bytes)
    with tempfile.NamedTemporaryFile(suffix=".dbf", delete=False) as f:
        f.write(dbf_bytes)
        tmp = Path(f.name)
    try:
        if max_rows is None:
            records = list(dbfread.DBF(str(tmp), encoding="latin-1"))
        else:
            records = []
            for rec in dbfread.DBF(str(tmp), encoding="latin-1"):
                records.append(rec)
                if len(records) >= max_rows:
                    break
        return pd.DataFrame(records)
    finally:
        tmp.unlink(missing_ok=True)


# ── Low-level fetch: single file ──────────────────────────────────────────────

def _http_get(http_dir: str, filename: str) -> bytes | None:
    for variant in _name_variants(filename):
        url = f"{HTTP_MIRROR}/{http_dir}{variant}"
        try:
            resp = requests.get(url, timeout=120, stream=True)
            if resp.status_code == 200:
                return resp.content
        except Exception:
            continue
    return None


def _ftp_get(ftp_dir: str, filename: str) -> bytes | None:
    try:
        with ftplib.FTP(FTP_HOST, timeout=60) as ftp:
            ftp.login()
            ftp.set_pasv(True)
            for variant in _name_variants(filename):
                buf = io.BytesIO()
                try:
                    ftp.retrbinary(f"RETR {ftp_dir}{variant}", buf.write)
                    return buf.getvalue()
                except ftplib.error_perm:
                    continue
    except Exception:
        pass
    return None


# ── HTTP strategies ───────────────────────────────────────────────────────────

def _try_http_sih(state: str, year: int, max_rows: int | None = None) -> pd.DataFrame | None:
    cfg = FTP_CONFIG["SIH"]
    dfs: list[pd.DataFrame] = []
    total = 0
    for month in range(1, 13):
        filename = _resolve_filename(cfg, state, year, month)
        raw = _http_get(cfg["http_path"], filename)
        if raw:
            try:
                remaining = (max_rows - total) if max_rows else None
                part = _dbc_to_df(raw, max_rows=remaining)
                del raw  # free compressed bytes ASAP
                dfs.append(part)
                total += len(part)
                if max_rows and total >= max_rows:
                    break  # enough rows — skip remaining months
            except Exception:
                pass
    return pd.concat(dfs, ignore_index=True) if dfs else None


def _try_http_annual(system: str, state: str, year: int, max_rows: int | None = None) -> pd.DataFrame | None:
    cfg = FTP_CONFIG[system]
    filename = _resolve_filename(cfg, state, year)

    # Systems with multiple candidate paths (SINAN_DENG, SINAN_HANS, etc.)
    if "http_paths" in cfg:
        for http_dir in cfg["http_paths"]:
            raw = _http_get(http_dir, filename)
            if raw:
                df = _dbc_to_df(raw, max_rows=max_rows)
                if cfg.get("national"):
                    df = _filter_national(df, cfg, state)
                return df
        return None

    # SINAN_TB year-dependent path
    if system == "SINAN_TB":
        _, http_dir = _sinan_tb_dirs(year)
    else:
        http_dir = cfg["http_path"]

    raw = _http_get(http_dir, filename)
    if raw:
        df = _dbc_to_df(raw, max_rows=max_rows)
        if cfg.get("national"):
            df = _filter_national(df, cfg, state)
        return df
    return None


# ── FTP strategies ────────────────────────────────────────────────────────────

def _try_ftp_sih(state: str, year: int, max_rows: int | None = None) -> pd.DataFrame | None:
    cfg = FTP_CONFIG["SIH"]
    dfs: list[pd.DataFrame] = []
    total = 0
    try:
        with ftplib.FTP(FTP_HOST, timeout=60) as ftp:
            ftp.login()
            ftp.set_pasv(True)
            for month in range(1, 13):
                filename = _resolve_filename(cfg, state, year, month)
                for variant in _name_variants(filename):
                    buf = io.BytesIO()
                    try:
                        ftp.retrbinary(f"RETR {cfg['ftp_path']}{variant}", buf.write)
                        remaining = (max_rows - total) if max_rows else None
                        part = _dbc_to_df(buf.getvalue(), max_rows=remaining)
                        dfs.append(part)
                        total += len(part)
                        break
                    except ftplib.error_perm:
                        continue
                if max_rows and total >= max_rows:
                    break
    except Exception:
        pass
    return pd.concat(dfs, ignore_index=True) if dfs else None


def _try_ftp_annual(system: str, state: str, year: int, max_rows: int | None = None) -> pd.DataFrame | None:
    cfg = FTP_CONFIG[system]
    filename = _resolve_filename(cfg, state, year)

    # Systems with multiple candidate paths
    if "ftp_paths" in cfg:
        for ftp_dir in cfg["ftp_paths"]:
            raw = _ftp_get(ftp_dir, filename)
            if raw:
                df = _dbc_to_df(raw, max_rows=max_rows)
                if cfg.get("national"):
                    df = _filter_national(df, cfg, state)
                return df
        return None

    # SINAN_TB year-dependent path
    if system == "SINAN_TB":
        ftp_dir, _ = _sinan_tb_dirs(year)
    else:
        ftp_dir = cfg["ftp_path"]

    raw = _ftp_get(ftp_dir, filename)
    if raw:
        df = _dbc_to_df(raw, max_rows=max_rows)
        if cfg.get("national"):
            df = _filter_national(df, cfg, state)
        return df
    return None


# ── Strategy 0: pySUS (Linux/Mac only) ───────────────────────────────────────

def _try_pysus(system: str, state: str, year: int) -> pd.DataFrame | None:
    try:
        if system == "SIH":
            from pysus.online_data.SIH import download
            raw = download(states=state.upper(), years=year, months=list(range(1, 13)))
        elif system == "SIM":
            from pysus.online_data.SIM import download
            raw = download(groups="CID10", states=state.upper(), years=year)
        elif system == "SINASC":
            from pysus.online_data.SINASC import download
            raw = download(states=state.upper(), years=year)
        elif system == "SINAN_TB":
            from pysus.online_data.SINAN import download
            raw = download(disease="TB", years=year)
        else:
            return None

        if hasattr(raw, "to_dataframe"):
            return raw.to_dataframe()
        if isinstance(raw, pd.DataFrame):
            return raw
    except Exception:
        pass
    return None


# ── Public API ────────────────────────────────────────────────────────────────

def fetch(
    system: str,
    state: str,
    year: int,
    progress_callback=None,
    max_rows: int | None = None,
) -> pd.DataFrame:
    """Download DataSUS data for a system/state/year with cache and fallback.

    max_rows: cap rows read during decompression to avoid OOM on large files
    (e.g. SIH SP). When set, the result is NOT cached because it is partial.
    """
    cache = _cache_path(system, state, year)
    is_monthly = FTP_CONFIG.get(system, {}).get("monthly", False)

    # 0. Cache hit (only when not limiting rows)
    if cache.exists() and max_rows is None:
        if progress_callback:
            progress_callback(1.0, f"{system} {state} {year} (cache local)")
        return pd.read_parquet(cache)

    errors = []

    # 1. pySUS (Linux/Mac)
    if progress_callback:
        progress_callback(0.05, f"{system} {state} {year} — tentando pySUS...")
    df = _try_pysus(system, state, year)
    if df is not None and len(df) > 0:
        if max_rows and len(df) > max_rows:
            df = df.sample(n=max_rows, random_state=42).reset_index(drop=True)
        if progress_callback:
            progress_callback(1.0, f"{system} {state} {year} via pySUS")
        return df if max_rows else _save(df, system, state, year)
    errors.append("pySUS indisponivel")

    # 2. HTTP mirror
    if progress_callback:
        progress_callback(0.3, f"{system} {state} {year} — tentando mirror HTTP...")
    df = (
        _try_http_sih(state, year, max_rows=max_rows)
        if is_monthly
        else _try_http_annual(system, state, year, max_rows=max_rows)
    )
    if df is not None and len(df) > 0:
        if progress_callback:
            progress_callback(1.0, f"{system} {state} {year} via HTTP mirror")
        return df if max_rows else _save(df, system, state, year)
    errors.append("mirror HTTP falhou")

    # 3. FTP direto
    if progress_callback:
        progress_callback(0.6, f"{system} {state} {year} — tentando FTP DataSUS...")
    df = (
        _try_ftp_sih(state, year, max_rows=max_rows)
        if is_monthly
        else _try_ftp_annual(system, state, year, max_rows=max_rows)
    )
    if df is not None and len(df) > 0:
        if progress_callback:
            progress_callback(1.0, f"{system} {state} {year} via FTP")
        return df if max_rows else _save(df, system, state, year)
    errors.append("FTP DataSUS falhou")

    # 4. Manual upload required
    raise ManualUploadRequired(system, state, year, reason=" | ".join(errors))


def load_from_csv(csv_bytes: bytes, system: str, state: str, year: int) -> pd.DataFrame:
    """Load a manually-uploaded CSV, cache to parquet, return DataFrame."""
    df = pd.read_csv(io.BytesIO(csv_bytes), encoding="latin-1", low_memory=False, sep=None, engine="python")
    return _save(df, system, state, year)


def fetch_multi(
    system: str,
    states: list[str],
    years: list[int],
    progress_callback=None,
) -> pd.DataFrame:
    dfs = []
    total = len(states) * len(years)
    for i, (state, year) in enumerate((s, y) for s in states for y in years):
        def cb(pct, msg, _i=i, _t=total):
            if progress_callback:
                progress_callback((_i + pct) / _t, msg)
        dfs.append(fetch(system, state, year, cb))
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def cached_files() -> list[str]:
    return [p.name for p in RAW_DIR.glob("*.parquet")]


# ── Legacy aliases ────────────────────────────────────────────────────────────
fetch_sih      = lambda s, y, cb=None: fetch("SIH",      s, y, cb)
fetch_sim      = lambda s, y, cb=None: fetch("SIM",      s, y, cb)
fetch_sinasc   = lambda s, y, cb=None: fetch("SINASC",   s, y, cb)
fetch_sinan_tb = lambda s, y, cb=None: fetch("SINAN_TB", s, y, cb)
