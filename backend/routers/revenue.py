from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from database import engine
from schemas import RevenueSummary

router = APIRouter(prefix="/revenue", tags=["Revenue"])


@router.get("", response_model=RevenueSummary)
def revenue_summary():
    """Backed by mv_live_revenue_summary — refreshed every 5 min."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT ticket_revenue, food_revenue, refreshed_at
                FROM mv_live_revenue_summary
            """)).fetchone()
            return dict(result._mapping) if result else {}
    except Exception:
        raise HTTPException(status_code=503, detail="Revenue data unavailable")


@router.get("/sales")
def food_sales():
    """Backed by mv_food_sales_summary — refreshed every 15 min."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT stall_id, total_revenue, total_quantity, refreshed_at
                FROM mv_food_sales_summary
                ORDER BY total_revenue DESC
            """))
            return [dict(row._mapping) for row in result]
    except Exception:
        raise HTTPException(status_code=503, detail="Food sales data unavailable")


@router.get("/event-performance")
def event_performance():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT event_id, revenue, tickets_sold
                FROM vw_event_revenue
                ORDER BY revenue DESC
            """))
            return [dict(row._mapping) for row in result]
    except Exception:
        raise HTTPException(status_code=503, detail="Event performance data unavailable")
