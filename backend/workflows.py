"""
EventSphereX — Module 4: Workflow Automation

Five workflows react to conditions already tracked in Postgres:

  1. Overcrowding        — density > 85%           (crowd_alerts, from trigger)
  2. Payment Failure     — failure RATE > 10%       (computed live, no trigger for rates)
  3. Emergency            — Critical incident        (emergency_tickets, from trigger)
  4. Food Stall           — avg wait > 15 min         (computed live, no existing trigger)
  5. App Reliability      — crash RATE > threshold    (computed live, no trigger for rates)

Every action taken is written to workflow_actions so it's auditable.
A short cooldown per (workflow_name, reference_id) stops a still-true
condition from re-logging the same action every poll cycle.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import text
from database import engine

POLL_SECONDS = 60          # how often the engine checks all 5 workflows
COOLDOWN_MINUTES = 5        # don't re-log the same alert within this window
RATE_WINDOW = "15 minutes"  # lookback window for rate-based workflows (2 & 5)
CRASH_RATE_THRESHOLD = 5.0  # % — "Crash Rate > Threshold" from the brief; tune as needed


def _log_action(conn, workflow_name, trigger_condition, action_taken, reference_id=None):
    conn.execute(text("""
        INSERT INTO workflow_actions (workflow_name, trigger_condition, action_taken, reference_id)
        VALUES (:workflow_name, :trigger_condition, :action_taken, :reference_id)
    """), {
        "workflow_name": workflow_name,
        "trigger_condition": trigger_condition,
        "action_taken": action_taken,
        "reference_id": reference_id,
    })


def _recently_logged(conn, workflow_name, reference_id=None) -> bool:
    row = conn.execute(text("""
        SELECT 1 FROM workflow_actions
        WHERE workflow_name = :workflow_name
          AND (reference_id = :reference_id OR (:reference_id IS NULL AND reference_id IS NULL))
          AND created_at > NOW() - make_interval(mins => :cooldown)
        LIMIT 1
    """), {
        "workflow_name": workflow_name,
        "reference_id": reference_id,
        "cooldown": COOLDOWN_MINUTES,
    }).fetchone()
    return row is not None


# ---------------------------------------------------------------
# Workflow 1 — Overcrowding (density > 85%)
# Reads rows the fn_overcrowding_alert trigger already inserted.
# ---------------------------------------------------------------
def workflow_overcrowding(conn):
    rows = conn.execute(text("""
        SELECT alert_id, zone_id, crowd_density
        FROM crowd_alerts
        WHERE resolved = FALSE
    """)).fetchall()

    for r in rows:
        ref = f"crowd_alert_{r.alert_id}"
        if not _recently_logged(conn, "Overcrowding Workflow", ref):
            _log_action(
                conn, "Overcrowding Workflow",
                f"Zone {r.zone_id} density {r.crowd_density}% > 85%",
                "Send Alert; Open Additional Gates",
                ref,
            )


# ---------------------------------------------------------------
# Workflow 2 — Payment Failure (failure RATE > 10%)
# The DB trigger fires per failed transaction; this computes the
# rate over a rolling window, which the brief actually asks for.
# ---------------------------------------------------------------
def workflow_payment_failure(conn):
    row = conn.execute(text(f"""
        SELECT
            COUNT(*) FILTER (WHERE transaction_status = 'Failed') AS failed,
            COUNT(*) AS total
        FROM silver.payment_transactions
        WHERE timestamp > (SELECT MAX(timestamp) FROM silver.payment_transactions) - INTERVAL '{RATE_WINDOW}'
    """)).fetchone()

    if row and row.total:
        failure_rate = (row.failed / row.total) * 100
        if failure_rate > 10 and not _recently_logged(conn, "Payment Failure Workflow"):
            _log_action(
                conn, "Payment Failure Workflow",
                f"Failure rate {failure_rate:.1f}% > 10% (last {RATE_WINDOW} of data)",
                "Notify Finance Team; Switch Gateway",
            )


# ---------------------------------------------------------------
# Workflow 3 — Emergency (severity = Critical)
# Reads rows the fn_emergency_escalation trigger already inserted.
# ---------------------------------------------------------------
def workflow_emergency(conn):
    rows = conn.execute(text("""
        SELECT ticket_id, incident_id
        FROM emergency_tickets
        WHERE status = 'Open'
    """)).fetchall()

    for r in rows:
        ref = f"emergency_ticket_{r.ticket_id}"
        if not _recently_logged(conn, "Emergency Workflow", ref):
            _log_action(
                conn, "Emergency Workflow",
                f"Critical incident {r.incident_id}",
                "Notify Security Team; Escalate Command Center",
                ref,
            )


# ---------------------------------------------------------------
# Workflow 4 — Food Stall Optimization (avg wait > 15 min)
# No DB trigger exists for this — computed live from silver.food_sales.
# ---------------------------------------------------------------
def workflow_food_stall(conn):
    rows = conn.execute(text(f"""
        SELECT stall_id, AVG(wait_time) AS avg_wait
        FROM silver.food_sales
        WHERE timestamp > (SELECT MAX(timestamp) FROM silver.food_sales) - INTERVAL '{RATE_WINDOW}'
        GROUP BY stall_id
        HAVING AVG(wait_time) > 15
    """)).fetchall()

    for r in rows:
        ref = f"stall_{r.stall_id}"
        if not _recently_logged(conn, "Food Stall Optimization Workflow", ref):
            _log_action(
                conn, "Food Stall Optimization Workflow",
                f"Stall {r.stall_id} avg wait {r.avg_wait:.1f} min > 15 min",
                "Open Additional Counters",
                ref,
            )


# ---------------------------------------------------------------
# Workflow 5 — App Reliability (crash RATE > threshold)
# The DB trigger fires per crash; this computes the rate, which
# is what "Crash Rate > Threshold" in the brief actually means.
# ---------------------------------------------------------------
def workflow_app_reliability(conn):
    row = conn.execute(text(f"""
        SELECT
            COUNT(*) FILTER (WHERE crash_flag IS TRUE) AS crashes,
            COUNT(*) AS total
        FROM silver.event_app_logs
        WHERE timestamp > (SELECT MAX(timestamp) FROM silver.event_app_logs) - INTERVAL '{RATE_WINDOW}'
    """)).fetchone()

    if row and row.total:
        crash_rate = (row.crashes / row.total) * 100
        if crash_rate > CRASH_RATE_THRESHOLD and not _recently_logged(conn, "App Reliability Workflow"):
            _log_action(
                conn, "App Reliability Workflow",
                f"Crash rate {crash_rate:.1f}% > {CRASH_RATE_THRESHOLD}% (last {RATE_WINDOW} of data)",
                "Notify Technical Team",
            )


def run_all_workflows():
    try:
        with engine.begin() as conn:
            workflow_overcrowding(conn)
            workflow_payment_failure(conn)
            workflow_emergency(conn)
            workflow_food_stall(conn)
            workflow_app_reliability(conn)
    except Exception as e:
        # Never let a bad poll crash the scheduler thread — log and try again next cycle.
        print(f"[workflows] poll failed: {e}")


scheduler = BackgroundScheduler()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            run_all_workflows, "interval",
            seconds=POLL_SECONDS, id="workflow_engine", replace_existing=True,
        )
        scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)