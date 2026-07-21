from kafka import KafkaConsumer
import json
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from backend.kafka_store import kafka_messages

consumer = KafkaConsumer(
    "ticket-bookings",
    "payment-transactions",
    "crowd-tracking",
    "gate-scans",
    "food-sales",
    "app-logs",
    "incident-logs",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    consumer_timeout_ms=3000,
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("Waiting for Kafka messages...")

for msg in consumer:

    kafka_messages.append(msg.value)

    if len(kafka_messages) > 50:
        kafka_messages.pop(0)

    print("\n" + "=" * 50)
    print("TOPIC:", msg.topic)
    print("MESSAGE:", msg.value)