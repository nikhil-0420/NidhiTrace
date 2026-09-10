from pydantic import BaseModel
from typing import Optional
from datetime import date

class WorkOut(BaseModel):
    id: int
    work_id: str
    work_category: str
    state: str
    ida: str
    mp_name: str
    constituency: str
    sanction_amount: float
    gap_days: float
    flag_delay: bool
    flag_amount: bool
    flag_mp_drift: bool
    flag_isolation_forest: bool
    n_flags: int
    is_high_severity: bool
    dq_flag: bool
    class Config:
        from_attributes = True

class DossierOut(WorkOut):
    work_status: Optional[str] = None
    sanction_date: Optional[date] = None
    lok_sabha_term: Optional[str] = None
    gap_robust_z: Optional[float] = None
    amount_robust_z: Optional[float] = None
    mp_drift_robust_z: Optional[float] = None
    mp_baseline_eligible: Optional[bool] = None
    dq_implausible_amount: bool = False
    dq_possible_miscategorization: bool = False
    dq_stale_status: bool = False
    dq_reason: Optional[str] = None
    explanation: Optional[str] = None

class SeverityBreakdown(BaseModel):
    total_works: int
    flagged_count: int
    high_severity_count: int
    delay_flagged: int
    amount_flagged: int
    mp_drift_flagged: int
    isolation_forest_flagged: int
    dq_flagged_count: int
    dq_implausible_amount_count: int
    dq_possible_miscategorization_count: int
    dq_stale_status_count: int