-- ============================================================
-- EventSphereX — Module 1, Task 1: Enterprise Views
-- Run against PostgreSQL. These are the source of truth for
-- aggregation logic — the API layer should never re-derive
-- these numbers in Python, only SELECT from here.
-- ============================================================

-- View 1 — Event Revenue
CREATE OR REPLACE VIEW vw_event_revenue AS
SELECT
    event_id,
    SUM(ticket_price)  AS revenue,
    COUNT(*)           AS tickets_sold
FROM silver.ticket_booking
WHERE booking_status = 'Confirmed'
GROUP BY event_id;

-- View 2 — Crowd Density
CREATE OR REPLACE VIEW vw_crowd_density AS
SELECT
    zone_id,
    AVG(crowd_density) AS avg_density,
    MAX(crowd_density) AS peak_density,
    AVG(heatmap_score)  AS heatmap_score,
    CASE
        WHEN AVG(crowd_density) > 80 THEN 'High'
        WHEN AVG(crowd_density) > 60 THEN 'Medium'
        ELSE 'Low'
    END AS risk_level
FROM silver.crowd_tracking
GROUP BY zone_id;

-- View 3 — Gate Operations
CREATE OR REPLACE VIEW vw_gate_operations AS
SELECT
    gate_id,
    COUNT(*)                                   AS throughput,
    ROUND(AVG(queue_time)::numeric, 2)         AS avg_wait,
    ROUND(
        100.0 * SUM(CASE WHEN validation_status = 'Success' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0), 2
    )                                           AS scan_success_rate,
    CASE WHEN AVG(queue_time) > 20 THEN 'Congested' ELSE 'Normal' END AS status
FROM silver.entry_gate_scans
GROUP BY gate_id;

-- View 4 — Incident Management
CREATE OR REPLACE VIEW vw_incident_management AS
SELECT
    zone_id,
    incident_type,
    severity_level,
    COUNT(*)                                    AS incident_count,
    ROUND(AVG(response_time)::numeric, 2)       AS avg_response_time,
    SUM(CASE WHEN resolution_status = 'Resolved' THEN 1 ELSE 0 END) AS resolved_count,
    SUM(CASE WHEN resolution_status <> 'Resolved' THEN 1 ELSE 0 END) AS open_count
FROM silver.incident_logs
GROUP BY zone_id, incident_type, severity_level;

-- View 5 — Food & Merchandise Performance
CREATE OR REPLACE VIEW vw_food_merch_performance AS
SELECT
    stall_id,
    product_category,
    SUM(quantity)                          AS units_sold,
    SUM(revenue)                           AS revenue,
    ROUND(AVG(wait_time)::numeric, 2)      AS avg_wait_time
FROM silver.food_sales
GROUP BY stall_id, product_category;
