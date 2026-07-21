from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from database import engine
from schemas import WorkflowAction

router = APIRouter(tags=["Workflow Automation"])


@router.get("/workflows", response_model=list[WorkflowAction])
def list_workflow_actions(limit: int = 50):
    """Most recent actions taken by the Module 4 automation engine (workflows.py)."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT action_id, workflow_name, trigger_condition, action_taken,
                       reference_id, created_at
                FROM workflow_actions
                ORDER BY created_at DESC
                LIMIT :limit
            """), {"limit": limit})
            return [dict(row._mapping) for row in result]
    except Exception:
        raise HTTPException(status_code=503, detail="Workflow log unavailable")
