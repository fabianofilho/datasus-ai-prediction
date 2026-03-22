"""Record linkage between DataSUS systems.

Strategy:
1. Deterministic: exact match on CNS or CPF (when available).
2. Probabilistic fallback: recordlinkage library with Jaro-Winkler name
   similarity + exact date + sex match.

Returns a DataFrame with matched pairs: (index_left, index_right).
"""

from __future__ import annotations

import pandas as pd


def link_deterministic(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_id: str,
    right_id: str,
    id_cols: list[str] = ["CNS", "CPF"],
) -> pd.DataFrame:
    """Link two DataFrames by exact match on identifier columns.

    Returns a DataFrame with columns [left_id, right_id].
    """
    pairs = []
    for col in id_cols:
        l_col = next((c for c in left.columns if col in c.upper()), None)
        r_col = next((c for c in right.columns if col in c.upper()), None)
        if l_col is None or r_col is None:
            continue

        l_valid = left[[left_id, l_col]].dropna(subset=[l_col])
        l_valid = l_valid[l_valid[l_col].astype(str).str.len() > 5]
        r_valid = right[[right_id, r_col]].dropna(subset=[r_col])
        r_valid = r_valid[r_valid[r_col].astype(str).str.len() > 5]

        merged = l_valid.merge(
            r_valid,
            left_on=l_col,
            right_on=r_col,
            how="inner",
        )[[left_id, right_id]]
        pairs.append(merged)

    if not pairs:
        return pd.DataFrame(columns=[left_id, right_id])

    result = pd.concat(pairs).drop_duplicates()
    return result


def link_probabilistic(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_id: str,
    right_id: str,
    left_name_col: str | None = None,
    right_name_col: str | None = None,
    left_dob_col: str | None = None,
    right_dob_col: str | None = None,
    left_sex_col: str | None = None,
    right_sex_col: str | None = None,
    threshold: float = 0.85,
    max_candidates: int = 500_000,
) -> pd.DataFrame:
    """Probabilistic linkage using the recordlinkage library.

    Uses blocking on birth-year + name Soundex to reduce candidate pairs,
    then scores with Jaro-Winkler (name) + exact date + sex.

    Returns matched pairs DataFrame with columns [left_id, right_id, score].
    """
    try:
        import recordlinkage
        from recordlinkage.preprocessing import phonetic
    except ImportError:
        raise ImportError(
            "recordlinkage not installed. Run: pip install recordlinkage"
        )

    left = left.copy().reset_index(drop=True)
    right = right.copy().reset_index(drop=True)

    # ── Blocking ───────────────────────────────────────────────────────────────
    indexer = recordlinkage.Index()

    if left_dob_col and right_dob_col:
        # Block on birth year
        left["_birth_year"] = pd.to_datetime(left[left_dob_col], errors="coerce").dt.year
        right["_birth_year"] = pd.to_datetime(right[right_dob_col], errors="coerce").dt.year
        indexer.block("_birth_year")
    elif left_name_col and right_name_col:
        # Block on first letter of name
        left["_name_block"] = left[left_name_col].astype(str).str[0]
        right["_name_block"] = right[right_name_col].astype(str).str[0]
        indexer.block("_name_block")
    else:
        indexer.full()

    candidate_pairs = indexer.index(left, right)
    if len(candidate_pairs) > max_candidates:
        candidate_pairs = candidate_pairs[:max_candidates]

    # ── Comparison ────────────────────────────────────────────────────────────
    compare = recordlinkage.Compare()

    if left_name_col and right_name_col:
        compare.string(left_name_col, right_name_col, method="jarowinkler", label="name_score")

    if left_dob_col and right_dob_col:
        compare.exact(left_dob_col, right_dob_col, label="dob_exact")

    if left_sex_col and right_sex_col:
        compare.exact(left_sex_col, right_sex_col, label="sex_exact")

    features = compare.compute(candidate_pairs, left, right)

    # ── Classification ────────────────────────────────────────────────────────
    features["score"] = features.mean(axis=1)
    matched = features[features["score"] >= threshold].reset_index()
    matched.columns = ["left_idx", "right_idx", *features.columns[:-1], "score"]

    # Map back to original IDs
    matched[left_id] = left.loc[matched["left_idx"], left_id].values
    matched[right_id] = right.loc[matched["right_idx"], right_id].values

    return matched[[left_id, right_id, "score"]].drop_duplicates(subset=[left_id])


def link_sih_sim(
    sih: pd.DataFrame,
    sim: pd.DataFrame,
    window_days: int = 30,
) -> pd.DataFrame:
    """Link SIH discharges to SIM deaths within `window_days`.

    Returns sih with added column 'death_date' and 'linked_death' (0/1).
    """
    sih = sih.copy()
    sim = sim.copy()

    # Deterministic first
    det = link_deterministic(sih, sim, left_id="N_AIH", right_id="NUMERODO")

    if len(det) > 0:
        sim_dates = sim.set_index("NUMERODO")["DTOBITO"]
        det["death_date"] = det["NUMERODO"].map(sim_dates)
        merged = sih.merge(det[["N_AIH", "death_date"]], on="N_AIH", how="left")
    else:
        merged = sih.copy()
        merged["death_date"] = pd.NaT

    # Flag deaths within window
    if "DT_SAIDA" in merged.columns:
        delta = (merged["death_date"] - merged["DT_SAIDA"]).dt.days
        merged["linked_death"] = (
            delta.notna() & (delta >= 0) & (delta <= window_days)
        ).astype(int)
    else:
        merged["linked_death"] = 0

    return merged


def _filter_neonatal_deaths(sim: pd.DataFrame, window_days: int = 28) -> pd.DataFrame:
    """Keep only SIM records that are plausibly neonatal deaths.

    Uses the IDADE encoding (1XX=hours, 2XX=days, 3XX=months, 4XX=years).
    For window_days=28 we keep hours, days ≤ 28, and months = 0 (< 1 month).
    Falls back to keeping all records if IDADE is missing.
    """
    if "IDADE" not in sim.columns:
        return sim
    s = pd.to_numeric(sim["IDADE"], errors="coerce")
    unit = (s // 100).fillna(-1).astype(int)
    value = (s % 100).fillna(999)
    neonatal = (
        (unit == 1)                                    # hours → always < 28 days
        | ((unit == 2) & (value <= window_days))       # days ≤ window
        | ((unit == 3) & (value == 0))                 # months = 0 (<1 month)
    )
    filtered = sim[neonatal]
    # If filter is too aggressive (no results), return all
    return filtered if len(filtered) > 0 else sim


def link_sinasc_sim(
    sinasc: pd.DataFrame,
    sim: pd.DataFrame,
    window_days: int = 28,
) -> pd.DataFrame:
    """Link SINASC births to SIM neonatal deaths within `window_days`.

    Strategy (memory-safe):
    1. Filter SIM to neonatal deaths only (~3-5k records vs ~330k total).
    2. Build a set of (DTNASC, SEXO, PESO) keys present in neonatal deaths.
    3. Flag SINASC records whose key appears in that set as neonatal deaths.

    This avoids any full cartesian / probabilistic join.
    Returns sinasc with added column 'neonatal_death' (0/1).
    """
    sinasc = sinasc.copy()
    sim_neonatal = _filter_neonatal_deaths(sim, window_days)

    # Build join keys — use whatever fields are available in both DataFrames
    join_cols = []
    for col in ["DTNASC", "SEXO", "PESO"]:
        if col in sinasc.columns and col in sim_neonatal.columns:
            join_cols.append(col)

    if not join_cols:
        # No common fields — cannot link; assume no neonatal deaths
        sinasc["neonatal_death"] = 0
        return sinasc

    # Normalise join key columns
    def _normalise(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
        df = df[cols].copy()
        if "DTNASC" in cols:
            df["DTNASC"] = pd.to_datetime(df["DTNASC"], errors="coerce")
        if "PESO" in cols:
            df["PESO"] = pd.to_numeric(df["PESO"], errors="coerce")
        if "SEXO" in cols:
            df["SEXO"] = df["SEXO"].astype(str).str.strip()
        return df

    left_keys = _normalise(sinasc, join_cols)
    right_keys = _normalise(sim_neonatal, join_cols).drop_duplicates()

    # Flag: SINASC row is a neonatal death if its key exists in SIM neonatal
    indicator = left_keys.merge(right_keys.assign(_match=1), on=join_cols, how="left")
    sinasc["neonatal_death"] = indicator["_match"].fillna(0).astype(int).values

    return sinasc
