import psycopg2
import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8")
)

conn = psycopg2.connect(
    host="localhost",
    database="eventspherex",
    user="postgres",
    password="vibha22"
)

cur = conn.cursor()

TABLES = {
    "silver.ticket_booking": "ticket-bookings",
    "silver.payment_transactions": "payment-transactions",
    "silver.crowd_tracking": "crowd-tracking",
    "silver.entry_gate_scans": "gate-scans",
    "silver.food_sales": "food-sales",
    "silver.event_app_logs": "app-logs",
    "silver.incident_logs": "incident-logs"
}


while True:

    for table, topic in TABLES.items():

        if table == "silver.ticket_booking":
            cur.execute("SELECT * FROM silver.ticket_booking WHERE booking_id LIKE 'BK%' LIMIT 5")

        elif table == "silver.payment_transactions":
            cur.execute("SELECT * FROM silver.payment_transactions WHERE transaction_id LIKE 'TXN%' LIMIT 5")

        elif table == "silver.crowd_tracking":
            cur.execute("SELECT * FROM silver.crowd_tracking WHERE crowd_event_id LIKE 'CRD%' LIMIT 5")

        elif table == "silver.entry_gate_scans":
            cur.execute("SELECT * FROM silver.entry_gate_scans WHERE scan_id LIKE 'SCN%' LIMIT 5")

        elif table == "silver.food_sales":
            cur.execute("SELECT * FROM silver.food_sales LIMIT 5")

        elif table == "silver.event_app_logs":
            cur.execute("SELECT * FROM silver.event_app_logs WHERE activity_id LIKE 'ACT%' LIMIT 5")

        elif table == "silver.incident_logs":
            cur.execute("SELECT * FROM silver.incident_logs WHERE incident_id LIKE 'INC%' LIMIT 5")

        print(table)
        print(cur.query)
        columns = [desc[0] for desc in cur.description]

        rows = cur.fetchall()
        print(rows)
        for row in rows:
            message = {
                "current_topic": topic,
                "data": dict(zip(columns, row))
            }

            producer.send(topic, message)

            producer.flush()

            print(f"Sent: {topic}")

            time.sleep(2)