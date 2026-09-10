from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Date
from app.db.database import Base

class Work(Base):
    __tablename__ = "works"

    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(String, index=True)
    work_category = Column(String)
    state = Column(String, index=True)
    ida = Column(String)
    mp_name = Column(String, index=True)
    constituency = Column(String)
    sanction_amount = Column(Float)
    gap_days = Column(Float)

    # NEW — needed for dq_stale_status; also useful generally for dossier display
    work_status = Column(String, nullable=True)
    sanction_date = Column(Date, nullable=True)
    lok_sabha_term = Column(String, nullable=True)

    flag_delay = Column(Boolean, default=False)
    flag_amount = Column(Boolean, default=False)
    flag_mp_drift = Column(Boolean, default=False)
    flag_isolation_forest = Column(Boolean, default=False)

    # n_flags/is_high_severity are 3-signal only (delay/amount/mp_drift) —
    # isolation forest stays an independent 4th check, per the
    # three-independent-triage-list design decision. Blending it in here
    # would make "high severity" mean something different from the
    # validated "compound" numbers on the slide.
    n_flags = Column(Integer, default=0)
    is_high_severity = Column(Boolean, default=False)

    # RENAMED from amount_deviation_pct / mp_drift_zscore: these are now
    # robust (median/MAD) z-scores in log space, matching
    # 03_synthetic_injection_validation.py exactly — not raw mean/std
    # deviation percentages. Renamed rather than reused so a stale
    # frontend/query can't silently misinterpret the new numbers as the
    # old percentage-based ones.
    gap_robust_z = Column(Float, nullable=True)
    amount_robust_z = Column(Float, nullable=True)
    mp_drift_robust_z = Column(Float, nullable=True)
    mp_baseline_eligible = Column(Boolean, default=False)

    # NEW — Data Quality Flags, the 4th independent triage list.
    # Deliberately separate from flag_delay/flag_amount/flag_mp_drift and
    # excluded from n_flags/is_high_severity: these are data-quality
    # issues, not irregularities.
    dq_implausible_amount = Column(Boolean, default=False)
    dq_possible_miscategorization = Column(Boolean, default=False)
    dq_stale_status = Column(Boolean, default=False)
    dq_flag = Column(Boolean, default=False)
    dq_reason = Column(Text, nullable=True)

    explanation = Column(Text, nullable=True)