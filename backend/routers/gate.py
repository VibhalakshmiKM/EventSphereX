from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from database import engine
from schemas import GateStatus

router = APIRouter(prefix="/gate", tags=["Gate Operations"])


@router.get("/performance", response_model=list[GateStatus])
def gate_performance():
    """Backed by mv_gate_performance_summary — refreshed every 2 min."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT gate_id, throughput, avg_wait, status, refreshed_at
                FROM mv_gate_performance_summary
                ORDER BY avg_wait DESC
            """))
            return [dict(row._mapping) for row in result]
    except Exception:
        raise HTTPException(status_code=503, detail="Gate performance data unavailable")


@router.get("/status")
def gate_status():
    """Live per-gate status derived from vw_gate_operations (no refresh lag, cheap view)."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT gate_id, status, scan_success_rate
                FROM vw_gate_operations
                ORDER BY gate_id
            """))
            return [dict(row._mapping) for row in result]
    except Exception:
        raise HTTPException(status_code=503, detail="Gate status unavailable")


@router.get("/queue")
def gate_queue():
    """Raw queue-time distribution for the last hour, used for the wait-time chart."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT gate_id, queue_time, scan_time
                FROM entry_gate_scans
                WHERE scan_time > NOW() - INTERVAL '1 hour'
                ORDER BY scan_time DESC
                LIMIT 200
            """))
            return [dict(row._mapping) for row in result]
    except Exception:
        raise HTTPException(status_code=503, detail="Gate queue data unavailable")
