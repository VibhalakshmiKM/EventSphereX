-- ============================================================
-- EventSphereX — Module 4: Workflow Automation
-- Log table for actions taken by the APScheduler-based
-- workflow engine (backend/workflows.py). Every automated
-- "Send Alert" / "Notify X" / "Open additional Y" is a row
-- here — this table IS the audit trail for Module 4.
-- ============================================================

CREATE TABLE IF NOT EXISTS workflow_actions (
    action_id         SERIAL PRIMARY KEY,
    workflow_name     VARCHAR(80)  NOT NULL,
    trigger_condition TEXT         NOT NULL,
    action_taken      TEXT         NOT NULL,
    reference_id      VARCHAR(120),   -- links back to the alert row that caused this, if any
    created_at        TIMESTAMP DEFAULT NOW()
);

-- Speeds up the cooldown check (same workflow+reference within last N minutes)
CREATE INDEX IF NOT EXISTS idx_workflow_actions_lookup
    ON workflow_actions (workflow_name, reference_id, created_at);
