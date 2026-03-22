"""DataSUS downloader with local parquet cache.

Download strategy (tried in order):
1. Cache hit  → load parquet from disk, skip download.
2. pySUS      → pysus>=1.0 (requires pyreaddbc, Mac/Linux only).
3. FTP + DBC  → download .dbc directly from DataSUS FTP via pyreaddbc.
4. Manual CSV → raise ManualUploadRequired so the UI can show a file uploader.
"""

from __future__ import annotations

import ftplib
import io
import os
import shutil
import tempfile
from dataclasses import dataclass
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

UF_CODE = {
    "RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15",
    "AP": "16", "TO": "17", "MA": "21", "PI": "22", "CE": "23",
    "RN": "24", "PB": "25", "PE": "26", "AL": "27", "SE": "28",
    "BA": "29", "MG": "31", "ES": "32", "RJ": "33", "SP": "35",
    "PR": "41", "SC": "42", "RS": "43", "MS": "50", "MT": "51",
    "GO": "52", "DF": "53",
}


@dataclass(frozen=True)
class FtpConfig:
    """FTP location and filename pattern for a DataSUS system.

    Patterns use str.format_map keys: {state}, {year}, {year2}, {month}.
    """
    path: str
    pattern: str
    monthly: bool = False

    def filenames(self, state: str, year: int) -> list[str]:
        ctx = {"state": state.upper(), "year": str(year), "year2": str(year)[-2:]}
        if self.monthly:
            return [self.pattern.format(**ctx, month=m) for m in range(1, 13)]
        return [self.pattern.format(**ctx)]


# Verified against live FTP (ftp.datasus.gov.br) on 2026-03
FTP_CONFIG: dict[str, FtpConfig] = {
    "SIH": FtpConfig(
        path="/dissemin/publicos/SIHSUS/200801_/Dados/",
        pattern="RD{state}{year2}{month:02d}.dbc",  # RDSP2301.dbc … RDSP2312.dbc
        monthly=True,
    ),
    "SIM": FtpConfig(
        path="/dissemin/publicos/SIM/CID10/DORES/",
        pattern="DO{state}{year}.dbc",  # DOSP2023.dbc
    ),
    "SINASC": FtpConfig(
        path="/dissemin/publicos/SINASC/NOV/DNRES/",
        pattern="DN{state}{year}.dbc",  # DNSP2022.dbc (max ~2022)
    ),
    "SINAN_TB": FtpConfig(
        path="/dissemin/publicos/SINAN/DADOS/FINAIS/",
        pattern="TUBEBR{year2}.dbc",  # national file, max ~2019
    ),
}


class ManualUploadRequired(Exception):
    """Raised when automatic download is not possible — user must upload CSV."""

    def __init__(self, system: str, state: str, year: int, reasons: list[str] | None = None):
        self.system = system
        self.state = state
        self.year = year
        self.reasons = reasons or []
        detail = (" Erros: " + " | ".join(self.reasons)) if self.reasons else ""
        super().__init__(
            f"Não foi possível baixar {system} {state} {year} automaticamente.{detail}"
        )


# ── Cache helpers ──────────────────────────────────────────────────────────────

def _cache_path(system: str, state: str, year: int) -> Path:
    return RAW_DIR / f"{system.lower()}_{state.upper()}_{year}.parquet"


def _save(df: pd.DataFrame, system: str, state: str, year: int) -> pd.DataFrame:
    df.to_parquet(_cache_path(system, state, year), index=False)
    return df


# ── Strategy 1: pySUS ─────────────────────────────────────────────────────────

def _pysus_to_df(result) -> pd.DataFrame:
    """Normalise pysus result (ParquetSet or list[ParquetSet]) to DataFrame."""
    if isinstance(result, list):
        return pd.concat([r.to_dataframe() for r in result], ignore_index=True)
    return result.to_dataframe()


def _try_pysus(system: str, state: str, year: int) -> tuple[pd.DataFrame | None, str | None]:
    """Download via pysus>=1.0. Uses a temp dir cleaned up on exit."""
    _DOWNLOADERS = {
        "SIH": lambda s, y, d: __import__("pysus.online_data", fromlist=["SIH"]).SIH.download(s, y, list(range(1, 13)),
                                                                                              "RD", data_dir=d),
        "SIM": lambda s, y, d: __import__("pysus.online_data", fromlist=["SIM"]).SIM.download("CID10", s, y,
                                                                                              data_dir=d),
        "SINASC": lambda s, y, d: __import__("pysus.online_data", fromlist=["SINASC"]).SINASC.download("DN", s, y,
                                                                                                       data_dir=d),
        "SINAN_TB": lambda s, y, d: __import__("pysus.online_data", fromlist=["SINAN"]).SINAN.download("TUBE", y,
                                                                                                       data_path=d),
    }
    if system not in _DOWNLOADERS:
        return None, f"pySUS: sistema '{system}' não suportado"

    tmpdir = tempfile.mkdtemp(prefix="pysus_")
    try:
        result = _DOWNLOADERS[system](state.upper(), year, tmpdir)
        df = _pysus_to_df(result)

        if system == "SINAN_TB":
            code = UF_CODE.get(state.upper(), "")
            uf_col = next((c for c in df.columns if "SG_UF" in c.upper() or "ID_MN_RESI" in c.upper()), None)
            if uf_col:
                df = df[df[uf_col].astype(str).str.startswith(code)]

        return df, None
    except Exception as e:
        return None, f"pySUS: {e}"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Strategy 2: FTP + DBC ─────────────────────────────────────────────────────

def _ftp_fetch_one(ftp: ftplib.FTP, path: str, filename: str) -> bytes | None:
    """Try downloading a file from FTP with case-variant fallbacks."""
    for name in (filename, filename.upper(), filename.lower()):
        buf = io.BytesIO()
        try:
            ftp.retrbinary(f"RETR {path}{name}", buf.write)
            return buf.getvalue()
        except ftplib.error_perm:
            continue
    return None


def _dbc_to_df(data: bytes) -> pd.DataFrame | None:
    """Convert DBC bytes → DataFrame via pyreaddbc."""
    try:
        import pyreaddbc
        fd, tmppath = tempfile.mkstemp(suffix=".dbc")
        try:
            os.write(fd, data)
            os.close(fd)
            return pyreaddbc.read_dbc(tmppath, encoding="latin-1")
        finally:
            os.unlink(tmppath)
    except Exception:
        return None


def _try_ftp(system: str, state: str, year: int) -> tuple[pd.DataFrame | None, str | None]:
    cfg = FTP_CONFIG[system]
    try:
        with ftplib.FTP(FTP_HOST, timeout=60) as ftp:
            ftp.login()
            dfs = [
                df
                for name in cfg.filenames(state, year)
                if (raw := _ftp_fetch_one(ftp, cfg.path, name))
                   and (df := _dbc_to_df(raw)) is not None
            ]
        if not dfs:
            return None, f"FTP: nenhum arquivo encontrado para {system} {state.upper()} {year}"
        return pd.concat(dfs, ignore_index=True), None
    except Exception as e:
        return None, f"FTP: {e}"


# ── Public API ────────────────────────────────────────────────────────────────

def fetch(system: str, state: str, year: int, progress_callback=None) -> pd.DataFrame:
    """Download DataSUS data for a system/state/year with cache and fallback."""
    cache = _cache_path(system, state, year)

    if cache.exists():
        if progress_callback:
            progress_callback(1.0, f"{system} {state} {year} (cache)")
        return pd.read_parquet(cache)

    reasons: list[str] = []

    if progress_callback:
        progress_callback(0.1, f"Tentando pySUS {system} {state} {year}...")
    df, err = _try_pysus(system, state, year)
    if df is not None and len(df) > 0:
        if progress_callback:
            progress_callback(1.0, f"{system} {state} {year} via pySUS ✓")
        return _save(df, system, state, year)
    if err:
        reasons.append(err)

    if progress_callback:
        progress_callback(0.4, f"Tentando FTP {system} {state} {year}...")
    df, err = _try_ftp(system, state, year)
    if df is not None and len(df) > 0:
        if progress_callback:
            progress_callback(1.0, f"{system} {state} {year} via FTP ✓")
        return _save(df, system, state, year)
    if err:
        reasons.append(err)

    raise ManualUploadRequired(system, state, year, reasons)


def load_from_csv(csv_bytes: bytes, system: str, state: str, year: int) -> pd.DataFrame:
    """Load a manually-uploaded CSV, save to parquet cache, return DataFrame."""
    df = pd.read_csv(io.BytesIO(csv_bytes), encoding="latin-1", low_memory=False)
    return _save(df, system, state, year)


def fetch_multi(
    system: str,
    states: list[str],
    years: list[int],
    progress_callback=None,
) -> pd.DataFrame:
    """Fetch and concatenate data for multiple states/years."""
    total = len(states) * len(years)
    dfs = [
        fetch(system, state, year,
              (lambda pct, msg, i=i: progress_callback((i + pct) / total, msg)) if progress_callback else None)
        for i, (state, year) in enumerate((s, y) for s in states for y in years)
    ]
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def cached_files() -> list[str]:
    return [p.name for p in RAW_DIR.glob("*.parquet")]
