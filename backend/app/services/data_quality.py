"""
Data Quality Flags — the 4th independent triage list.

Surfaces likely SOURCE-DATA quality issues as their own auditable list,
separate from anomaly detection entirely. NOT scored as irregularities
and NOT included in n_flags/is_high_severity (see rules_engine.py).

Ports data_quality_flags() from 03_synthetic_injection_validation.py.
Requires work_status, sanction_date, and lok_sabha_term to be populated
on the Work row (added to models.py alongside this file) — these come
from the same merged source data the validation scripts use.
"""
import pandas as pd

MIN_PLAUSIBLE_AMOUNT = 1000            # Rs. floor — see manual review: confirmed real
                                         # records with amounts like Rs 3.92, Rs 3.50
                                         # present in BOTH recommended and sanctioned
                                         # amount columns in the raw source data
CATEGORY_MISFIT_THRESHOLD = 5000001    # Rs 50L + 1 — avoids landing exactly on the
                                         # documented Rs 50L administrative slab value
                                         # (153 real records sit exactly at Rs 50,00,000)
STALE_STATUS_TERM = "17th"             # concluded term — status should be terminal by now
INCOMPLETE_STATUSES = [
    "Physical Inspection", "Vendor Identification",
    "Time Estimation", "Work partially Completed",
]
COMPLETION_RULE_OUTER_DAYS = 730       # 24 months


def data_quality_flags(df: pd.DataFrame, as_of_date=None) -> pd.DataFrame:
    df = df.copy()

    df["dq_implausible_amount"] = (
        df["sanction_amount"].notna() & (df["sanction_amount"] < MIN_PLAUSIBLE_AMOUNT)
    )

    df["dq_possible_miscategorization"] = (
        (df["work_category"] == "Normal/Others")
        & (df["sanction_amount"] >= CATEGORY_MISFIT_THRESHOLD)
    )

    if as_of_date is None:
        as_of_date = df["sanction_date"].max()
    days_since_sanction = (as_of_date - df["sanction_date"]).dt.days
    is_incomplete_status = df["work_status"].isin(INCOMPLETE_STATUSES)
    df["dq_stale_status"] = (
        is_incomplete_status
        & (df["lok_sabha_term"] == STALE_STATUS_TERM)
        & (days_since_sanction > COMPLETION_RULE_OUTER_DAYS)
    )

    def reason(row):
        reasons = []
        if row["dq_implausible_amount"]:
            reasons.append(
                f"Sanction amount (Rs {row['sanction_amount']:.2f}) implausibly low "
                f"for described work — likely source data-entry error"
            )
        if row["dq_possible_miscategorization"]:
            reasons.append(
                f"Large amount (Rs {row['sanction_amount']:,.0f}) recorded under generic "
                f"'Normal/Others' category — possible miscategorization, review for reassignment"
            )
        if row["dq_stale_status"]:
            reasons.append(
                f"Work Status ('{row['work_status']}') still non-terminal more than 24 months "
                f"after sanction, from the concluded 17th Lok Sabha term — likely stale portal "
                f"data rather than an active delay"
            )
        return "; ".join(reasons) if reasons else ""

    df["dq_flag"] = (
        df["dq_implausible_amount"]
        | df["dq_possible_miscategorization"]
        | df["dq_stale_status"]
    )
    df["dq_reason"] = df.apply(reason, axis=1)

    return df