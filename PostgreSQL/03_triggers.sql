-- ============================================================
-- EventSphereX — Module 1, Task 3: Triggers + alert tables
-- These are what feed the Emergency Control Center and the
-- workflow automations described in Module 4 of the brief.
-- ============================================================

CREATE TABLE IF NOT EXISTS crowd_alerts (
    alert_id     SERIAL PRIMARY KEY,
    zone_id      INT NOT NULL,
    crowd_density NUMERIC,
    created_at   TIMESTAMP DEFAULT NOW(),
    resolved     BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS payment_incidents (
    incident_id   SERIAL PRIMARY KEY,
    transaction_id INT,
    created_at    TIMESTAMP DEFAULT NOW(),
    resolved      BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS gate_alerts (
    alert_id    SERIAL PRIMARY KEY,
    gate_id     INT NOT NULL,
    queue_time  NUMERIC,
    created_at  TIMESTAMP DEFAULT NOW(),
    resolved    BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS emergency_tickets (
    ticket_id   SERIAL PRIMARY KEY,
    incident_id INT,
    created_at  TIMESTAMP DEFAULT NOW(),
    status      VARCHAR(20) DEFAULT 'Open'
);

CREATE TABLE IF NOT EXISTS technical_incidents (
    incident_id SERIAL PRIMARY KEY,
    activity_id INT,
    created_at  TIMESTAMP DEFAULT NOW(),
    resolved    BOOLEAN DEFAULT FALSE
);

-- Trigger 1 — Overcrowding Alert (density > 85%)
CREATE OR REPLACE FUNCTION fn_overcrowding_alert() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.crowd_density > 85 THEN
        INSERT INTO crowd_alerts (zone_id, crowd_density) VALUES (NEW.zone_id, NEW.crowd_density);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_overcrowding_alert
AFTER INSERT ON silver.crowd_tracking
FOR EACH ROW EXECUTE FUNCTION fn_overcrowding_alert();

-- Trigger 2 — Payment Failure Alert
CREATE OR REPLACE FUNCTION fn_payment_failure_alert() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.transaction_status = 'Failed' THEN
        INSERT INTO payment_incidents (transaction_id) VALUES (NEW.transaction_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_payment_failure_alert
AFTER INSERT ON silver.payment_transactions
FOR EACH ROW EXECUTE FUNCTION fn_payment_failure_alert();

-- Trigger 3 — Gate Congestion Alert (queue_time > 20 min)
CREATE OR REPLACE FUNCTION fn_gate_congestion_alert() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.queue_time > 20 THEN
        INSERT INTO gate_alerts (gate_id, queue_time) VALUES (NEW.gate_id, NEW.queue_time);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_gate_congestion_alert
AFTER INSERT ON silver.entry_gate_scans
FOR EACH ROW EXECUTE FUNCTION fn_gate_congestion_alert();

-- Trigger 4 — Emergency Escalation (severity = 'Critical')
CREATE OR REPLACE FUNCTION fn_emergency_escalation() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.severity_level = 'Critical' THEN
        INSERT INTO emergency_tickets (incident_id) VALUES (NEW.incident_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_emergency_escalation
AFTER INSERT ON silver.incident_logs
FOR EACH ROW EXECUTE FUNCTION fn_emergency_escalation();

-- Trigger 5 — App Crash Trigger
CREATE OR REPLACE FUNCTION fn_app_crash_trigger() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.crash_flag IS TRUE THEN
        INSERT INTO technical_incidents (activity_id) VALUES (NEW.activity_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_app_crash
AFTER INSERT ON silver.event_app_logs
FOR EACH ROW EXECUTE FUNCTION fn_app_crash_trigger();
