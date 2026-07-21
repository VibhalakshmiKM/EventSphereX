from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from database import engine
from schemas import CommandCenterSummary

router = APIRouter(tags=["Command Center"])


@router.get("/dashboard", response_model=CommandCenterSummary)
def dashboard():
    """
    Single low-cost summary for the Command Center page. Pulls from the
    same materialized views the domain pages use, so the top-level KPIs
    never drift from the detail pages underneath them.
    """
    try:
        with engine.connect() as conn:
            tickets = conn.execute(text(
                "SELECT COALESCE(SUM(tickets_sold),0), COALESCE(SUM(revenue),0) FROM vw_event_revenue"
            )).fetchone()

            crowd = conn.execute(text(
                "SELECT COALESCE(SUM(visitors),0) FROM mv_zone_occupancy_summary"
            )).scalar()

            incidents = conn.execute(text(
                "SELECT COUNT(*) FROM incident_logs WHERE resolution_status <> 'Resolved'"
            )).scalar()

            queue = conn.execute(text(
                "SELECT ROUND(AVG(avg_wait)::numeric, 2) FROM mv_gate_performance_summary"
            )).scalar()

            return {
                "tickets_sold": tickets[0] if tickets else 0,
                "revenue": tickets[1] if tickets else 0,
                "active_crowd": crowd or 0,
                "incidents": incidents or 0,
                "queue_time": queue,
            }
    except Exception:
        raise HTTPException(status_code=503, detail="Dashboard data unavailable")
