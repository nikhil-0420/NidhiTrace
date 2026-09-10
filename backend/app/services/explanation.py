def generate_explanation(row) -> str:
    reasons = []
    if row.get("flag_delay"):
        reasons.append(f"work has been delayed {int(row['gap_days'])} days beyond the normal recommend-to-sanction window")
    if row.get("flag_amount"):
        z_amt = row.get("amount_robust_z")
        reasons.append(f"sanctioned amount is {abs(z_amt):.1f} standard deviations from the category norm (log scale)" if z_amt is not None else "sanctioned amount flagged as a category outlier")
    if row.get("flag_mp_drift"):
        z = row.get("mp_drift_robust_z")
        reasons.append(f"amount is {abs(z):.1f} standard deviations from this MP's own historical norm for this category" if z is not None else "flagged for MP baseline drift")

    if not reasons:
        return "No anomaly flags triggered."
    prefix = "High severity — multiple factors: " if row.get("is_high_severity") else "Flagged: "
    return prefix + "; ".join(reasons) + "."