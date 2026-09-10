"""
Endpoints for anomaly/flagged-case data.
TODO: GET /anomalies (list flagged works, filter by severity)
TODO: GET /anomalies/{work_id} (dossier: flags + explanation)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Work
from app.models.schemas import WorkOut, DossierOut, SeverityBreakdown
from sqlalchemy import func, case

router = APIRouter()

@router.get("/", response_model=list[WorkOut])
def list_anomalies(
    signal: str = Query("delay", pattern="^(delay|amount|mp_drift|isolation_forest|high_severity|data_quality)$"),
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Work)
    if signal == "delay":
        q = q.filter(Work.flag_delay == True).order_by(Work.gap_days.desc())
    elif signal == "amount":
        q = q.filter(Work.flag_amount == True).order_by(func.abs(Work.amount_robust_z).desc())
    elif signal == "mp_drift":
        q = q.filter(Work.flag_mp_drift == True).order_by(func.abs(Work.mp_drift_robust_z).desc())
    elif signal == "isolation_forest":
        q = q.filter(Work.flag_isolation_forest == True)
    elif signal == "high_severity":
        q = q.filter(Work.is_high_severity == True)
    elif signal == "data_quality":
        q = q.filter(Work.dq_flag == True)
    return q.limit(limit).all()

@router.get("/{work_id}", response_model=DossierOut)
def get_dossier(work_id: str, db: Session = Depends(get_db)):
    return db.query(Work).filter(Work.work_id == work_id).first()

@router.get("/summary/breakdown", response_model=SeverityBreakdown)
def severity_breakdown(db: Session = Depends(get_db)):
    row = db.query(
        func.count().label("total_works"),
        func.sum(case((Work.n_flags > 0, 1), else_=0)).label("flagged_count"),
        func.sum(case((Work.is_high_severity == True, 1), else_=0)).label("high_severity_count"),
        func.sum(case((Work.flag_delay == True, 1), else_=0)).label("delay_flagged"),
        func.sum(case((Work.flag_amount == True, 1), else_=0)).label("amount_flagged"),
        func.sum(case((Work.flag_mp_drift == True, 1), else_=0)).label("mp_drift_flagged"),
        func.sum(case((Work.flag_isolation_forest == True, 1), else_=0)).label("isolation_forest_flagged"),
        func.sum(case((Work.dq_flag == True, 1), else_=0)).label("dq_flagged_count"),
        func.sum(case((Work.dq_implausible_amount == True, 1), else_=0)).label("dq_implausible_amount_count"),
        func.sum(case((Work.dq_possible_miscategorization == True, 1), else_=0)).label("dq_possible_miscategorization_count"),
        func.sum(case((Work.dq_stale_status == True, 1), else_=0)).label("dq_stale_status_count"),
    ).one()
    return SeverityBreakdown(**row._asdict())