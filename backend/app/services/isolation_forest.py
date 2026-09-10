"""
Statistical outlier layer using scikit-learn's IsolationForest.
Runs alongside the 3 rule-based signals as a 4th, independent check —
catches multivariate outliers the single-variable rules might miss
(e.g. a combination of moderate delay + moderate amount deviation
that's individually unremarkable but jointly unusual).

CHANGED: features are now the robust z-scores (gap_robust_z,
amount_robust_z, mp_drift_robust_z) instead of raw gap_days/
sanction_amount/amount_deviation_pct. Raw sanction_amount in particular
broke cross-category comparability — a legitimate multi-crore highway
project would look identical to a genuine outlier next to a routine
hand-pump repair, since IsolationForest has no notion of "outlier
relative to this category." The z-scores already encode that context,
matching what 03_synthetic_injection_validation.py's isolation_forest_score()
uses.

NOTE: this must run AFTER flag_delay/flag_amount/flag_mp_drift in
rules_engine.run_all_flags(), since it depends on their z-score outputs.
"""
import pandas as pd
from sklearn.ensemble import IsolationForest

CONTAMINATION = 0.05
RANDOM_SEED = 42


def flag_isolation_forest(df: pd.DataFrame) -> pd.Series:
    features = df[["gap_robust_z", "amount_robust_z", "mp_drift_robust_z"]].fillna(0)
    model = IsolationForest(contamination=CONTAMINATION, random_state=RANDOM_SEED)
    predictions = model.fit_predict(features)
    return predictions == -1