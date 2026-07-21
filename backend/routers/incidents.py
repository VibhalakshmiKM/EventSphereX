from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from database import engine
from schemas import Incident, IncidentCreate, ResolveResponse

router = APIRouter(prefix="/incident", tags=["Incident Management"])


@router.get("s", response_model=list[Incident])  # GET /incidents
def list_incidents(limit: int = 100, offset: int = 0):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT incident_id, zone_id, incident_type, severity_level,
                       response_time, resolution_status
                FROM incident_logs
                ORDER BY incident_id DESC
                LIMIT :limit OFFSET :offset
            """), {"limit": limit, "offset": offset})
            return [dict(row._mapping) for row in result]
    except Exception:
        raise HTTPException(status_code=503, detail="Incident data unavailable")


@router.post("", response_model=Incident)  # POST /incident
def create_incident(payload: IncidentCreate):
    try:
        with engine.begin() as conn:  # begin() commits automatically on success
            result = conn.execute(text("""
                INSERT INTO incident_logs (zone_id, incident_type, severity_level, resolution_status)
                VALUES (:zone_id, :incident_type, :severity_level, 'Open')
                RETURNING incident_id, zone_id, incident_type, severity_level, response_time, resolution_status
            """), payload.model_dump())
            return dict(result.fetchone()._mapping)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not create incident")


@router.put("/resolve/{incident_id}", response_model=ResolveResponse)  # PUT /incident/resolve
def resolve_incident(incident_id: int):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("""
                UPDATE incident_logs
                SET resolution_status = 'Resolved'
                WHERE incident_id = :id
                RETURNING incident_id, resolution_status
            """), {"id": incident_id})
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Incident not found")
            return dict(row._mapping)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Could not resolve incident")