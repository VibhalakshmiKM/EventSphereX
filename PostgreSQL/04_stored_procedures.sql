-- ============================================================
-- EventSphereX — Module 1, Task 2: Stored Procedures
-- Source tables live in `silver` (cleaned data). Output report
-- tables are created unprefixed in `public`, same as the views
-- in 01_views.sql, so no Python/router changes are needed.
-- ============================================================

-- Procedure 1 — Daily Event Report
-- CALL sp_daily_event_report();
-- select * from daily_event_report;
CREATE OR REPLACE PROCEDURE sp_daily_event_report()
LANGUAGE plpgsql
AS $$
BEGIN
    DROP TABLE IF EXISTS daily_event_report;
    CREATE TABLE daily_event_report AS
    SELECT
        (SELECT COUNT(*) FROM silver.ticket_booking WHERE booking_status = 'Confirmed')            AS total_bookings,
        (SELECT COALESCE(SUM(ticket_price), 0) FROM silver.ticket_booking WHERE booking_status = 'Confirmed') AS total_revenue,
        (SELECT COUNT(*) FROM silver.crowd_tracking)                                                AS crowd_events,
        (SELECT COUNT(*) FROM silver.incident_logs)                                                 AS total_incidents,
        (SELECT COALESCE(SUM(revenue), 0) FROM silver.food_sales)                                   AS food_sales_revenue,
        NOW()                                                                                       AS generated_at;
END;
$$;

-- Procedure 2 — Crowd Risk Score
-- CALL sp_crowd_risk_score();
-- Logic per brief: Crowd Density + Queue Length + Incident Count -> Zone Risk Score
CREATE OR REPLACE PROCEDURE sp_crowd_risk_score()
LANGUAGE plpgsql
AS $$
BEGIN
    DROP TABLE IF EXISTS crowd_risk_score;
    CREATE TABLE crowd_risk_score AS
    SELECT
        c.zone_id,
        ROUND(AVG(c.crowd_density)::numeric, 2)                       AS avg_density,
        COUNT(c.crowd_event_id)                                       AS crowd_count,
        ROUND(COALESCE(AVG(g.queue_time), 0)::numeric, 2)             AS avg_queue_time,
        COALESCE(i.incident_count, 0)                                 AS incident_count,
        ROUND(
            (AVG(c.crowd_density)
             + COALESCE(AVG(g.queue_time), 0)
             + COALESCE(i.incident_count, 0))::numeric / 3
        , 2)                                                          AS zone_risk_score
    FROM silver.crowd_tracking c
    LEFT JOIN silver.entry_gate_scans g ON g.gate_id = c.zone_id
    LEFT JOIN (
        SELECT zone_id, COUNT(*) AS incident_count
        FROM silver.incident_logs
        GROUP BY zone_id
    ) i ON i.zone_id = c.zone_id
    GROUP BY c.zone_id, i.incident_count;
END;
$$;

-- Procedure 3 — Dynamic Ticket Pricing
-- CALL sp_dynamic_pricing();
-- Logic per brief: Demand up + Remaining seats down -> increase price.
-- Demand proxy = bookings per event; scarcity proxy = confirmed share of bookings for that event.
CREATE OR REPLACE PROCEDURE sp_dynamic_pricing()
LANGUAGE plpgsql
AS $$
BEGIN
    DROP TABLE IF EXISTS dynamic_pricing;
    CREATE TABLE dynamic_pricing AS
    WITH demand AS (
        SELECT
            event_id,
            COUNT(*)                                                       AS total_bookings,
            SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END)  AS confirmed_bookings
        FROM silver.ticket_booking
        GROUP BY event_id
    )
    SELECT
        tb.booking_id,
        tb.event_id,
        tb.ticket_price,
        d.total_bookings,
        ROUND(
            tb.ticket_price *
            (1 + LEAST(0.30, GREATEST(0,
                (d.confirmed_bookings::numeric / NULLIF(d.total_bookings, 0)) - 0.5
            )))
        , 2)                                                              AS dynamic_price
    FROM silver.ticket_booking tb
    JOIN demand d ON d.event_id = tb.event_id
    WHERE tb.booking_status = 'Confirmed';
END;
$$;

-- Procedure 4 — Event Health Score
-- CALL sp_event_health_score();
-- Output: Revenue Score, Safety Score, Engagement Score, Operations Score
CREATE OR REPLACE PROCEDURE sp_event_health_score()
LANGUAGE plpgsql
AS $$
BEGIN
    DROP TABLE IF EXISTS event_health_score;
    CREATE TABLE event_health_score AS
    SELECT
        ROUND(
            (SELECT AVG(ticket_price)
             FROM silver.ticket_booking
             WHERE booking_status = 'Confirmed')::numeric
        , 2)                                                              AS revenue_score,
        ROUND(
            (100 -
             (SELECT AVG(crowd_density)
              FROM silver.crowd_tracking))::numeric
        , 2)                                                              AS safety_score,
        ROUND(
            (SELECT AVG(click_count)
             FROM silver.app_activity_logs)::numeric
        , 2)                                                              AS engagement_score,
        ROUND(
            (100 -
             (SELECT AVG(queue_time)
              FROM silver.entry_gate_scans))::numeric
        , 2)                                                              AS operations_score,
        NOW()                                                             AS generated_at;
END;
$$;

-- Procedure 5 — Fan Experience Score
-- CALL sp_fan_experience();
-- Based on: Queue Time, App Performance, Crowd Density, Food Wait Time
CREATE OR REPLACE PROCEDURE sp_fan_experience()
LANGUAGE plpgsql
AS $$
BEGIN
    DROP TABLE IF EXISTS fan_experience_score;
    CREATE TABLE fan_experience_score AS
    SELECT
        ROUND(
            (
                (100 - (SELECT AVG(queue_time) FROM silver.entry_gate_scans))
                + (SELECT AVG(click_count) / 1000.0 FROM silver.app_activity_logs)
                + (100 - (SELECT AVG(crowd_density) FROM silver.crowd_tracking))
                + (100 - (SELECT AVG(wait_time) FROM silver.food_sales))
            )::numeric / 4
        , 2)                                                              AS fan_experience_score,
        NOW()                                                             AS generated_at;
END;
$$;
