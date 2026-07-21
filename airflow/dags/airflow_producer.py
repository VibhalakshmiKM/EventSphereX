import psycopg2
import json
import time
from kafka import KafkaProducer

def run_streaming():

    producer = KafkaProducer(
        bootstrap_servers="kafka:29092",
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8")
    )

    conn = psycopg2.connect(
        host="host.docker.internal",
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
    for table in TABLES:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(table, cur.fetchone())

    for table, topic in TABLES.items():

        cur.execute(f"SELECT * FROM {table} LIMIT 5")

        columns = [desc[0] for desc in cur.description]

        for row in cur.fetchall():

            message = {
                "current_topic": topic,
                "data": dict(zip(columns, row))
            }

            producer.send(topic, message)
            producer.flush()

            print(f"Sent: {topic}")

            time.sleep(2)

    print("Streaming Completed")

if __name__ == "__main__":
    run_streaming()