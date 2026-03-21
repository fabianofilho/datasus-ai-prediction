"""pySUS download wrappers with local parquet cache.

Each fetch_* function:
1. Checks if data/raw/<system>_<state>_<year>.parquet already exists → load & return.
2. Otherwise downloads via pySUS, saves as parquet, returns DataFrame.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

STATES = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
    "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
    "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]


def _cache_path(system: str, state: str, year: int) -> Path:
    return RAW_DIR / f"{system.lower()}_{state.upper()}_{year}.parquet"


def _load_or_download(system: str, state: str, year: int, download_fn) -> pd.DataFrame:
    path = _cache_path(system, state, year)
    if path.exists():
        return pd.read_parquet(path)
    df = download_fn()
    df.to_parquet(path, index=False)
    return df


# ── SIH ───────────────────────────────────────────────────────────────────────

def fetch_sih(state: str, year: int, progress_callback=None) -> pd.DataFrame:
    """Download SIH-RD (hospitalization) data for a state/year."""
    def _download():
        from pySUS.online_data import SIH
        sih = SIH().load(state.upper(), year)
        return sih.to_dataframe()

    return _load_or_download("sih", state, year, _download)


# ── SIM ───────────────────────────────────────────────────────────────────────

def fetch_sim(state: str, year: int, progress_callback=None) -> pd.DataFrame:
    """Download SIM-DO (mortality) data for a state/year."""
    def _download():
        from pySUS.online_data import SIM
        sim = SIM().load(state.upper(), year)
        return sim.to_dataframe()

    return _load_or_download("sim", state, year, _download)


# ── SINASC ────────────────────────────────────────────────────────────────────

def fetch_sinasc(state: str, year: int, progress_callback=None) -> pd.DataFrame:
    """Download SINASC-DN (live births) data for a state/year."""
    def _download():
        from pySUS.online_data import SINASC
        sinasc = SINASC().load(state.upper(), year)
        return sinasc.to_dataframe()

    return _load_or_download("sinasc", state, year, _download)


# ── SINAN-TB ──────────────────────────────────────────────────────────────────

def fetch_sinan_tb(state: str, year: int, progress_callback=None) -> pd.DataFrame:
    """Download SINAN tuberculosis notification data for a state/year."""
    def _download():
        from pySUS.online_data import SINAN
        sinan = SINAN().load("TB", year)
        df = sinan.to_dataframe()
        # Filter to requested state if state column exists
        state_col = next((c for c in df.columns if "SG_UF" in c.upper() or "ID_UNIDADE" in c.upper()), None)
        if state_col and state.upper() != "BR":
            # SINAN national — state filter by residence UF code
            uf_map = _uf_to_code()
            code = uf_map.get(state.upper())
            if code and state_col in df.columns:
                df = df[df[state_col].astype(str).str.startswith(str(code))]
        return df

    return _load_or_download("sinan_tb", state, year, _download)


def _uf_to_code() -> dict[str, str]:
    """Map UF abbreviation → IBGE code prefix."""
    return {
        "RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15",
        "AP": "16", "TO": "17", "MA": "21", "PI": "22", "CE": "23",
        "RN": "24", "PB": "25", "PE": "26", "AL": "27", "SE": "28",
        "BA": "29", "MG": "31", "ES": "32", "RJ": "33", "SP": "35",
        "PR": "41", "SC": "42", "RS": "43", "MS": "50", "MT": "51",
        "GO": "52", "DF": "53",
    }


# ── Multi-state/year helpers ──────────────────────────────────────────────────

def fetch_multi(
    system: str,
    states: list[str],
    years: list[int],
    progress_callback=None,
) -> pd.DataFrame:
    """Fetch and concatenate data for multiple states and years."""
    fetchers = {
        "SIH": fetch_sih,
        "SIM": fetch_sim,
        "SINASC": fetch_sinasc,
        "SINAN_TB": fetch_sinan_tb,
    }
    fn = fetchers[system.upper()]
    dfs = []
    total = len(states) * len(years)
    for i, (state, year) in enumerate(
        (s, y) for s in states for y in years
    ):
        dfs.append(fn(state, year))
        if progress_callback:
            progress_callback((i + 1) / total, f"{system} {state} {year}")
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def cached_files() -> list[str]:
    """Return list of already-downloaded parquet files."""
    return [p.name for p in RAW_DIR.glob("*.parquet")]
