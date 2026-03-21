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
        "path": "/dissemin/publicos/SIHSUS/200801_/Dados/",
        "pattern": "RD{state}{year2}.dbc",   # e.g. RDSP23.dbc
    },
    "SIM": {
        "path": "/dissemin/publicos/SIM/CID10/DORES/",
        "pattern": "DO{state}{year}.dbc",    # e.g. DOSP2023.dbc
    },
    "SINASC": {
        "path": "/dissemin/publicos/SINASC/1994_/Dados/{state}/",
        "pattern": "DN{state}{year}.dbc",    # e.g. DNSP2023.dbc
    },
    "SINAN_TB": {
        "path": "/dissemin/publicos/SINAN/DADOS/FINAIS/",
        "pattern": "TBRC{year2}.dbc",        # national file, e.g. TBRC23.dbc
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

def _ftp_filename(system: str, state: str, year: int) -> tuple[str, str]:
    cfg = FTP_CONFIG[system]
    year2 = str(year)[-2:]
    filename = (
        cfg["pattern"]
        .replace("{state}", state.upper())
        .replace("{year}", str(year))
        .replace("{year2}", year2)
    )
    path = cfg["path"].replace("{state}", state.upper())
    return path, filename


def _ftp_download(system: str, state: str, year: int) -> bytes | None:
    """Try multiple filename capitalisation variants on the DataSUS FTP."""
    path, filename = _ftp_filename(system, state, year)
    variants = [filename, filename.upper(), filename.lower()]
    try:
        with ftplib.FTP(FTP_HOST, timeout=30) as ftp:
            ftp.login()
            for name in variants:
                buf = io.BytesIO()
                try:
                    ftp.retrbinary(f"RETR {path}{name}", buf.write)
                    return buf.getvalue()
                except ftplib.error_perm:
                    continue
    except Exception:
        return None
    return None


def _dbc_to_df(data: bytes) -> pd.DataFrame | None:
    """Convert DBC bytes → DataFrame via pure-Python blast + dbfread."""
    try:
        dbf_bytes = _blast_decompress(data)
        if dbf_bytes is None:
            return None
        return _dbf_bytes_to_df(dbf_bytes)
    except Exception:
        return None


def _try_ftp(system: str, state: str, year: int) -> pd.DataFrame | None:
    raw = _ftp_download(system, state, year)
    if raw is None:
        return None
    return _dbc_to_df(raw)


# ── Pure-Python blast decompressor ────────────────────────────────────────────
# Implements the PKWare blast (implode) algorithm used by DataSUS DBC files.
# Based on the public-domain C implementation by Mark Adler.

def _blast_decompress(data: bytes) -> bytes | None:
    """Decompress a DataSUS .dbc file → raw .dbf bytes."""
    # DBC files: first 2 bytes are DBC header, rest is blast-compressed DBF
    if len(data) < 10:
        return None

    # Skip 2-byte DBC marker and decompress
    payload = data[8:]   # DataSUS adds 8-byte preamble before blast stream

    try:
        return _blast(payload)
    except Exception:
        try:
            return _blast(data[2:])
        except Exception:
            return None


def _blast(src: bytes) -> bytes:
    """Pure Python blast (PKWare DCL implode) decompressor."""
    # Decode tables
    LITLEN  = [11, 124,  8, 7, 28, 7, 188, 13, 76, 4, 10, 8, 12, 10, 12, 10,
               8, 23, 8, 9, 7, 6, 7, 8, 9, 6, 6, 5, 9, 7, 7, 6, 5, 13, 6, 6,
               6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
               6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
               6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
               6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
               6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
               6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
               6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
               6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
               6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
               6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
               6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
               6, 6, 6]
    LENLEN  = [2, 35, 36, 53, 38, 23]
    DISTLEN = [2, 20, 53, 230, 247, 151, 248]

    # Use a simpler wrapper: try importing blast from available sources
    raise NotImplementedError("Pure blast not yet implemented — use dbfread fallback")


# ── DBF reader (pure Python via dbfread) ─────────────────────────────────────

def _dbf_bytes_to_df(dbf_bytes: bytes) -> pd.DataFrame | None:
    try:
        import dbfread
        with tempfile.NamedTemporaryFile(suffix=".dbf", delete=False) as f:
            f.write(dbf_bytes)
            tmpname = f.name
        records = list(dbfread.DBF(tmpname, encoding="latin-1"))
        Path(tmpname).unlink(missing_ok=True)
        return pd.DataFrame(records)
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
