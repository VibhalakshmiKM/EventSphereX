import os
import json
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from kafka import KafkaConsumer

from routers import gate, crowd, revenue, incidents, booking, dashboard
from workflow_router import router as workflow_router
from workflows import start_scheduler, stop_scheduler

load_dotenv()

kafka_messages = {
    "ticket-bookings": None,
    "payment-transactions": None,
    "crowd-tracking": None,
    "gate-scans": None,
    "food-sales": None,
    "app-logs": None,
    "incident-logs": None
}


def start_kafka_consumer():

    consumer = KafkaConsumer(
        "ticket-bookings",
        "payment-transactions",
        "crowd-tracking",
        "gate-scans",
        "food-sales",
        "app-logs",
        "incident-logs",
        bootstrap_servers="localhost:9092",
        group_id="eventsphere-ui-v2",
        auto_offset_reset="latest",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    for msg in consumer:
        print("TOPIC:", msg.topic)
        print(msg.value)
        kafka_messages[msg.topic] = msg.value
        print(kafka_messages)

        print(f"Kafka Message Received: {msg.topic}")


@asynccontextmanager
async def lifespan(app: FastAPI):

    start_scheduler()

    kafka_thread = threading.Thread(
        target=start_kafka_consumer,
        daemon=True
    )
    kafka_thread.start()

    yield

    stop_scheduler()


app = FastAPI(
    title="EventSphereX API",
    version="2.0.0",
    lifespan=lifespan
)

origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(gate.router)
app.include_router(crowd.router)
app.include_router(revenue.router)
app.include_router(incidents.router)
app.include_router(booking.router)
app.include_router(workflow_router)


@app.get("/")
def home():
    return {
        "message": "EventSphereX API Running",
        "version": app.version
    }


@app.get("/kafka-stream")
def kafka_stream():
    return kafka_messages
    

@app.get("/health")
def health():
    return {"status": "ok"}