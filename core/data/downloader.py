"""DataSUS downloader with local parquet cache.

Download strategy (tried in order):
1. Cache hit  → load parquet from disk, skip download.
2. pySUS      → if installed and pyreaddbc compiled (Linux/Mac).
3. FTP + DBC  → download .dbc directly from DataSUS FTP, decompress with
                 the pure-Python blast implementation bundled here.
4. Manual CSV → raise ManualUploadRequired so the UI can show a file uploader.
"""

from __future__ import annotations

import ftplib
import io
import struct
import tempfile
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

STATES = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
    "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
    "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]

FTP_HOST = "ftp.datasus.gov.br"

# FTP paths and filename patterns per system
FTP_CONFIG = {
    "SIH": {
        # Monthly files: RD{STATE}{YY}{MM}.dbc — download all 12 months
        "path": "/dissemin/publicos/SIHSUS/200801_/Dados/",
        "pattern": "RD{state}{year2}{month:02d}.dbc",  # e.g. RDSP2301.dbc
        "monthly": True,
    },
    "SIM": {
        "path": "/dissemin/publicos/SIM/CID10/DORES/",
        "pattern": "DO{state}{year}.dbc",    # e.g. DOSP2023.dbc
    },
    "SINASC": {
        # Real path: 1996_/Dados/DNRES/ (not per-state subdirectory)
        "path": "/dissemin/publicos/SINASC/1996_/Dados/DNRES/",
        "pattern": "DN{state}{year}.DBC",    # e.g. DNSP2023.DBC
    },
    "SINAN_DENG": {
        # National dengue file — FINAIS first, then PRELIM
        "paths": [
            "/dissemin/publicos/SINAN/DADOS/FINAIS/",
            "/dissemin/publicos/SINAN/DADOS/PRELIM/",
        ],
        "pattern": "DENGBR{year2}.dbc",
        "national": True,
        "uf_col": "SG_UF_NOT",
    },
    "SINAN_HANS": {
        # National Hansen's disease file — FINAIS first, then PRELIM
        "paths": [
            "/dissemin/publicos/SINAN/DADOS/FINAIS/",
            "/dissemin/publicos/SINAN/DADOS/PRELIM/",
        ],
        "pattern": "HANSBR{year2}.dbc",
        "national": True,
        "uf_col": "SG_UF_NOT",
    },
    "SINAN_TB": {
        "paths": [
            "/dissemin/publicos/SINAN/DADOS/PRELIM/",
            "/dissemin/publicos/SINAN/DADOS/FINAIS/",
        ],
        "pattern": "TUBEBR{year2}.dbc",
        "national": True,
        "uf_col": "SG_UF_NOT",
    },
    "SINAN_CHIK": {
        "paths": [
            "/dissemin/publicos/SINAN/DADOS/FINAIS/",
            "/dissemin/publicos/SINAN/DADOS/PRELIM/",
        ],
        "pattern": "CHIKBR{year2}.dbc",
        "national": True,
        "uf_col": "SG_UF_NOT",
    },
    "SINAN_VIOL": {
        "paths": [
            "/dissemin/publicos/SINAN/DADOS/FINAIS/",
            "/dissemin/publicos/SINAN/DADOS/PRELIM/",
        ],
        "pattern": "VIOLBR{year2}.dbc",
        "national": True,
        "uf_col": "SG_UF_NOT",
    },
    "SINAN_IEXO": {
        "paths": [
            "/dissemin/publicos/SINAN/DADOS/PRELIM/",
            "/dissemin/publicos/SINAN/DADOS/FINAIS/",
        ],
        "pattern": "IEXOBR{year2}.dbc",
        "national": True,
        "uf_col": "SG_UF_NOT",
    },
    "SINAN_AIDS": {
        "paths": [
            "/dissemin/publicos/SINAN/DADOS/PRELIM/",
            "/dissemin/publicos/SINAN/DADOS/FINAIS/",
        ],
        "pattern": "AIDABR{year2}.dbc",
        "national": True,
        "uf_col": "SG_UF_NOT",
    },
    "SINAN_SIFA": {
        # Sífilis adquirida
        "paths": [
            "/dissemin/publicos/SINAN/DADOS/PRELIM/",
            "/dissemin/publicos/SINAN/DADOS/FINAIS/",
        ],
        "pattern": "SIFABR{year2}.dbc",
        "national": True,
        "uf_col": "SG_UF_NOT",
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
    """Raised when automatic download is not possible — user must upload CSV."""
    def __init__(self, system: str, state: str, year: int):
        self.system = system
        self.state = state
        self.year = year
        super().__init__(
            f"Não foi possível baixar {system} {state} {year} automaticamente. "
            "Faça o download manual no TABNET e faça upload do CSV na plataforma."
        )


# ── Cache helpers ──────────────────────────────────────────────────────────────

def _cache_path(system: str, state: str, year: int) -> Path:
    return RAW_DIR / f"{system.lower()}_{state.upper()}_{year}.parquet"


def _save(df: pd.DataFrame, system: str, state: str, year: int) -> pd.DataFrame:
    df.to_parquet(_cache_path(system, state, year), index=False)
    return df


# ── Strategy 1: pySUS ─────────────────────────────────────────────────────────

def _try_pysus(system: str, state: str, year: int) -> pd.DataFrame | None:
    try:
        if system == "SIH":
            from pySUS.online_data import SIH
            return SIH().load(state.upper(), year).to_dataframe()
        if system == "SIM":
            from pySUS.online_data import SIM
            return SIM().load(state.upper(), year).to_dataframe()
        if system == "SINASC":
            from pySUS.online_data import SINASC
            return SINASC().load(state.upper(), year).to_dataframe()
        if system == "SINAN_TB":
            from pySUS.online_data import SINAN
            df = SINAN().load("TB", year).to_dataframe()
            code = UF_CODE.get(state.upper(), "")
            for col in df.columns:
                if "SG_UF" in col.upper() or "ID_MN_RESI" in col.upper():
                    df = df[df[col].astype(str).str.startswith(code)]
                    break
            return df
    except Exception:
        return None


# ── Strategy 2: FTP + DBC ─────────────────────────────────────────────────────

def _ftp_download_file(ftp: ftplib.FTP, path: str, filename: str) -> bytes | None:
    """Try exact filename + upper + lower variants on an open FTP connection."""
    for name in [filename, filename.upper(), filename.lower()]:
        buf = io.BytesIO()
        try:
            ftp.retrbinary(f"RETR {path}{name}", buf.write)
            return buf.getvalue()
        except ftplib.error_perm:
            continue
    return None


def _ftp_download(system: str, state: str, year: int) -> bytes | list[bytes] | None:
    """Download DBC file(s) from DataSUS FTP.

    Returns bytes for single-file systems, list[bytes] for monthly SIH,
    or None if not found.
    """
    cfg = FTP_CONFIG[system]
    year2 = str(year)[-2:]

    def _render(pattern: str, month: int = 1) -> str:
        return (
            pattern
            .replace("{state}", state.upper())
            .replace("{year}", str(year))
            .replace("{year2}", year2)
            .replace("{month:02d}", f"{month:02d}")
        )

    try:
        with ftplib.FTP(FTP_HOST, timeout=60) as ftp:
            ftp.login()

            # SIH: download all 12 monthly files
            if cfg.get("monthly"):
                results = []
                for m in range(1, 13):
                    data = _ftp_download_file(ftp, cfg["path"], _render(cfg["pattern"], month=m))
                    if data:
                        results.append(data)
                return results if results else None

            # SINAN_TB: try multiple base paths
            if "paths" in cfg:
                for base_path in cfg["paths"]:
                    data = _ftp_download_file(ftp, base_path, _render(cfg["pattern"]))
                    if data:
                        return data
                return None

            # Standard single-file
            return _ftp_download_file(ftp, cfg["path"], _render(cfg["pattern"]))

    except Exception:
        return None


def _dbc_to_df(data: bytes) -> pd.DataFrame | None:
    """Convert DBC bytes → DataFrame via pyreaddbc (dbc2dbf) + dbfread."""
    import os
    dbc_path = None
    dbf_path = None
    try:
        from pyreaddbc import dbc2dbf
        import dbfread

        with tempfile.NamedTemporaryFile(suffix=".dbc", delete=False) as f:
            f.write(data)
            dbc_path = f.name

        dbf_path = dbc_path.replace(".dbc", ".dbf")
        dbc2dbf(dbc_path, dbf_path)
        records = list(dbfread.DBF(dbf_path, encoding="latin-1"))
        return pd.DataFrame(records)
    except Exception:
        return None
    finally:
        for p in [dbc_path, dbf_path]:
            if p and os.path.exists(p):
                os.unlink(p)


def _try_ftp(system: str, state: str, year: int) -> pd.DataFrame | None:
    raw = _ftp_download(system, state, year)
    if raw is None:
        return None

    # SIH returns list of monthly bytes
    if isinstance(raw, list):
        dfs = [_dbc_to_df(chunk) for chunk in raw]
        dfs = [df for df in dfs if df is not None and len(df) > 0]
        return pd.concat(dfs, ignore_index=True) if dfs else None

    df = _dbc_to_df(raw)

    # National SINAN files — filter by UF using configured column or fallback detection
    if cfg.get("national") and df is not None:
        code = UF_CODE.get(state.upper(), "")
        if code:
            uf_col_hint = cfg.get("uf_col")
            filter_col = None
            if uf_col_hint and uf_col_hint in df.columns:
                filter_col = uf_col_hint
            else:
                for col in df.columns:
                    col_upper = col.upper()
                    if col_upper in ("SG_UF_NOT", "SG_UF") or "SG_UF" in col_upper:
                        filter_col = col
                        break
            if filter_col:
                df = df[df[filter_col].astype(str).str.strip() == str(int(code))]

    return df


# ── DBF reader (pure Python via dbfread) ─────────────────────────────────────

def _dbf_bytes_to_df(dbf_bytes: bytes) -> pd.DataFrame | None:
    try:
        import dbfread

        with tempfile.NamedTemporaryFile(suffix=".dbf", delete=False) as f:
            f.write(dbf_bytes)
            tmpname = f.name

        table = dbfread.DBF(tmpname, encoding="latin-1", char_decode_errors="replace")

        # Iterate record-by-record; skip records with bad date/value fields
        records = []
        it = iter(table)
        while True:
            try:
                record = next(it)
                records.append(dict(record))
            except StopIteration:
                break
            except Exception:
                continue  # skip malformed record (e.g. invalid date '****')

        Path(tmpname).unlink(missing_ok=True)
        return pd.DataFrame(records) if records else None
    except Exception:
        return None


# ── Public API ────────────────────────────────────────────────────────────────

def fetch(system: str, state: str, year: int, progress_callback=None) -> pd.DataFrame:
    """Download DataSUS data for a system/state/year with cache and fallback."""
    cache = _cache_path(system, state, year)

    # 1. Cache hit
    if cache.exists():
        if progress_callback:
            progress_callback(1.0, f"{system} {state} {year} (cache)")
        return pd.read_parquet(cache)

    if progress_callback:
        progress_callback(0.1, f"Tentando pySUS {system} {state} {year}...")

    # 2. pySUS
    df = _try_pysus(system, state, year)
    if df is not None and len(df) > 0:
        if progress_callback:
            progress_callback(1.0, f"{system} {state} {year} via pySUS ✓")
        return _save(df, system, state, year)

    if progress_callback:
        progress_callback(0.4, f"pySUS indisponível, tentando FTP {system} {state} {year}...")

    # 3. FTP + DBC
    df = _try_ftp(system, state, year)
    if df is not None and len(df) > 0:
        if progress_callback:
            progress_callback(1.0, f"{system} {state} {year} via FTP ✓")
        return _save(df, system, state, year)

    # 4. Manual upload required
    raise ManualUploadRequired(system, state, year)


def load_from_csv(csv_bytes: bytes, system: str, state: str, year: int) -> pd.DataFrame:
    """Load a manually-uploaded CSV, save to parquet cache, return DataFrame."""
    df = pd.read_csv(io.BytesIO(csv_bytes), encoding="latin-1", low_memory=False)
    _save(df, system, state, year)
    return df


def fetch_multi(
    system: str,
    states: list[str],
    years: list[int],
    progress_callback=None,
) -> pd.DataFrame:
    """Fetch and concatenate data for multiple states/years."""
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


# ── Legacy aliases (backward compat) ─────────────────────────────────────────
def fetch_sih(state, year, progress_callback=None):
    return fetch("SIH", state, year, progress_callback)

def fetch_sim(state, year, progress_callback=None):
    return fetch("SIM", state, year, progress_callback)

def fetch_sinasc(state, year, progress_callback=None):
    return fetch("SINASC", state, year, progress_callback)

def fetch_sinan_tb(state, year, progress_callback=None):
    return fetch("SINAN_TB", state, year, progress_callback)
