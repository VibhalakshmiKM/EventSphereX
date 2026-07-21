from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GateStatus(BaseModel):
    gate_id: str
    throughput: int
    avg_wait: float
    status: str
    refreshed_at: Optional[datetime] = None


class ZoneOccupancy(BaseModel):
    zone_id: str
    visitors: int
    avg_density: float
    heatmap_score: Optional[float] = None
    risk_level: str
    refreshed_at: Optional[datetime] = None


class RevenueSummary(BaseModel):
    ticket_revenue: float = 0
    food_revenue: float = 0
    refreshed_at: Optional[datetime] = None


class CommandCenterSummary(BaseModel):
    tickets_sold: int = 0
    revenue: float = 0
    active_crowd: int = 0
    incidents: int = 0
    queue_time: Optional[float] = None


class Incident(BaseModel):
    incident_id: int
    zone_id: str
    incident_type: str
    severity_level: str
    response_time: Optional[float] = None
    resolution_status: str


class IncidentCreate(BaseModel):
    zone_id: str
    incident_type: str
    severity_level: str


class ResolveResponse(BaseModel):
    incident_id: int
    resolution_status: str


class WorkflowAction(BaseModel):
    action_id: int
    workflow_name: str
    trigger_condition: str
    action_taken: str
    reference_id: Optional[str] = None
    created_at: Optional[datetime] = None

