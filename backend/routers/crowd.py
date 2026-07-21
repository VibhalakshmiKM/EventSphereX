from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from database import engine
from schemas import ZoneOccupancy

router = APIRouter(prefix="/crowd", tags=["Crowd Intelligence"])


@router.get("/live", response_model=list[ZoneOccupancy])
def crowd_live():
    """Backed by mv_zone_occupancy_summary — refreshed every 1 min."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT zone_id, visitors, avg_density, heatmap_score, risk_level, refreshed_at
                FROM mv_zone_occupancy_summary
                ORDER BY avg_density DESC
            """))
            return [dict(row._mapping) for row in result]
    except Exception:
        raise HTTPException(status_code=503, detail="Crowd data unavailable")


@router.get("/heatmap")
def crowd_heatmap():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT zone_id, heatmap_score
                FROM vw_crowd_density
                ORDER BY heatmap_score DESC
            """))
            return [dict(row._mapping) for row in result]
    except Exception:
        raise HTTPException(status_code=503, detail="Heatmap data unavailable")


@router.get("/risk-zones")
def crowd_risk_zones():
    """Zones currently above the overcrowding trigger threshold (density > 85)."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT zone_id, avg_density, risk_level
                FROM vw_crowd_density
                WHERE avg_density > 85
                ORDER BY avg_density DESC
            """))
            return [dict(row._mapping) for row in result]
    except Exception:
        raise HTTPException(status_code=503, detail="Risk zone data unavailable")
