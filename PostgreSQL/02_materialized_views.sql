-- ============================================================
-- EventSphereX — Module 1, Task 4: Materialized Views
-- These are what the "live" dashboards actually query.
-- Refresh cadence is enforced by a scheduler (pg_cron shown
-- below; swap for Airflow if that's your orchestrator).
-- ============================================================

-- MV 1 — Live Revenue Summary (refresh every 5 min)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_live_revenue_summary AS
SELECT
    COALESCE((SELECT SUM(ticket_price) FROM silver.ticket_booking WHERE booking_status = 'Confirmed'), 0) AS ticket_revenue,
    COALESCE((SELECT SUM(revenue) FROM silver.food_sales), 0)                                              AS food_revenue,
    NOW() AS refreshed_at;

-- MV 2 — Zone Occupancy Summary (refresh every 1 min)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_zone_occupancy_summary AS
SELECT
    zone_id,
    COUNT(DISTINCT user_id)            AS visitors,
    AVG(crowd_density)                 AS avg_density,
    AVG(heatmap_score)                 AS heatmap_score,
    CASE
        WHEN AVG(crowd_density) > 85 THEN 'High'
        WHEN AVG(crowd_density) > 60 THEN 'Medium'
        ELSE 'Low'
    END AS risk_level,
    NOW() AS refreshed_at
FROM silver.crowd_tracking
GROUP BY zone_id;

-- MV 3 — Gate Performance Summary (refresh every 2 min)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_gate_performance_summary AS
SELECT
    gate_id,
    COUNT(*)                                    AS throughput,
    ROUND(AVG(queue_time)::numeric, 2)         AS avg_wait,
    CASE WHEN AVG(queue_time) > 20 THEN 'Congested' ELSE 'Normal' END AS status,
    NOW() AS refreshed_at
FROM silver.entry_gate_scans
GROUP BY gate_id;

-- MV 4 — Food Sales Summary (refresh every 15 min)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_food_sales_summary AS
SELECT
    stall_id,
    SUM(revenue)   AS total_revenue,
    SUM(quantity)  AS total_quantity,
    NOW() AS refreshed_at
FROM silver.food_sales
GROUP BY stall_id;

-- ---- scheduled refresh (requires the pg_cron extension) ----
-- SELECT cron.schedule('refresh_revenue',  '*/5 * * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_live_revenue_summary');
-- SELECT cron.schedule('refresh_zones',    '* * * * *',   'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_zone_occupancy_summary');
-- SELECT cron.schedule('refresh_gates',    '*/2 * * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_gate_performance_summary');
-- SELECT cron.schedule('refresh_food',     '*/15 * * * *','REFRESH MATERIALIZED VIEW CONCURRENTLY mv_food_sales_summary');
-- Concurrent refresh requires a unique index on each matview — add one per key column if you enable this.
