"""
Real anomaly detection on the full merged dataset — no injection, no
synthetic data.

REPLACES the previous percentile-based version. That version used
mean/std thresholds for flag_amount (broken on right-skewed data — the
exact bug root-caused and fixed in 03_synthetic_injection_validation.py)
and a top-5%-by-construction percentile cutoff for all three signals
instead of an absolute severity threshold. This meant the live site's
flagged records — and the resulting recall/precision numbers — would
not match the validated Stage B bootstrap results (43.1% compound
recall, 86.0% any-flag recall, etc.) that the pitch deck cites.

This version ports the validated methodology exactly:
  - median/MAD ("modified z-score", Iglewicz & Hoaglin 1993) instead of
    mean/std, since MPLAD amounts are heavily right-skewed
  - amount-based signals (amount, mp_drift) computed in LOG SPACE, since
    amounts vary multiplicatively (hand pump vs. highway)
  - a fixed absolute threshold (ROBUST_Z_THRESH = 3.5) instead of a
    percentile cutoff, so "flagged" means "genuinely extreme" rather
    than "top 5% no matter how mild"
  - isolation_forest stays an independent 4th signal, NOT folded into
    n_flags/is_high_severity — see models.py comment for why
"""
import numpy as np
import pandas as pd
from app.services.isolation_forest import flag_isolation_forest

ROBUST_Z_THRESH = 3.5
MIN_MP_CAT_CELL_N = 10       # matches validation: covers 99.1% of records
MIN_SCALE_FRACTION = 0.02    # scale must be >= 2% of median, else cell is too degenerate to score
MAD_SCALE = 1.4826           # makes MAD consistent with std under normality
IQR_SCALE = 1.349            # IQR fallback when MAD == 0 (common under slab-value clustering)


def robust_center_scale(values: pd.Series) -> tuple:
    median = values.median()
    mad = (values - median).abs().median()
    scale = mad * MAD_SCALE
    if scale <= abs(median) * MIN_SCALE_FRACTION:
        q1, q3 = values.quantile([0.25, 0.75])
        scale = (q3 - q1) / IQR_SCALE
    if scale <= abs(median) * MIN_SCALE_FRACTION or pd.isna(scale):
        return median, np.nan  # too degenerate to score — excluded, not divided by ~0
    return median, scale


def log_amount(series: pd.Series) -> pd.Series:
    return np.log1p(series)


def group_robust_zscore(df: pd.DataFrame, value_col: str, group_cols) -> pd.DataFrame:
    stats = df.groupby(group_cols)[value_col].apply(
        lambda g: pd.Series(robust_center_scale(g), index=["_median", "_scale"])
    ).unstack()
    stats["_n"] = df.groupby(group_cols)[value_col].size()
    return stats


def flag_delay(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    median, scale = robust_center_scale(df["gap_days"])
    df["gap_robust_z"] = (df["gap_days"] - median) / scale
    df["flag_delay"] = df["gap_robust_z"] > ROBUST_Z_THRESH
    return df


def flag_amount(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["_log_amount"] = log_amount(df["sanction_amount"])
    cat_stats = group_robust_zscore(df, "_log_amount", "work_category")
    df = df.merge(cat_stats[["_median", "_scale"]], left_on="work_category", right_index=True, how="left")
    df["amount_robust_z"] = (df["_log_amount"] - df["_median"]) / df["_scale"]
    df["flag_amount"] = df["amount_robust_z"].abs() > ROBUST_Z_THRESH
    return df.drop(columns=["_median", "_scale"])


def flag_mp_drift(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mp_cat_stats = group_robust_zscore(df, "_log_amount", ["mp_name", "work_category"])
    df = df.merge(mp_cat_stats, left_on=["mp_name", "work_category"], right_index=True, how="left")
    df["mp_baseline_eligible"] = (df["_n"] >= MIN_MP_CAT_CELL_N) & df["_scale"].notna()
    df["mp_drift_robust_z"] = (df["_log_amount"] - df["_median"]) / df["_scale"]
    df["flag_mp_drift"] = df["mp_baseline_eligible"] & (df["mp_drift_robust_z"].abs() > ROBUST_Z_THRESH)
    return df.drop(columns=["_median", "_scale", "_n", "_log_amount"])


def run_all_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = flag_delay(df)
    df = flag_amount(df)
    df = flag_mp_drift(df)
    df["flag_isolation_forest"] = flag_isolation_forest(df)

    # 3-signal compound score only — isolation forest is reported and
    # filterable independently (see api/routes/anomalies.py's
    # "isolation_forest" signal option) but does not count toward
    # n_flags/is_high_severity. See models.py comment.
    df["n_flags"] = df[["flag_delay", "flag_amount", "flag_mp_drift"]].sum(axis=1)
    df["is_high_severity"] = df["n_flags"] >= 2
    return df