# EventSphereX

EventSphereX is an event operations and analytics platform that combines ETL, real-time Kafka streaming, REST APIs, operational dashboards, workflow automation, and business intelligence.

## Tech Stack

- Python, Pandas
- PostgreSQL
- Apache Kafka
- Apache Airflow
- FastAPI
- React.js
- Power BI
- Docker

## System Architecture



## ETL Pipeline

Seven event datasets are processed:

- Ticket Bookings
- Payments
- Crowd Tracking
- Gate Scans
- Food Sales
- App Logs
- Incident Logs

The ETL pipeline performs data inspection, cleaning, standardization, datetime conversion, validation, and loading into PostgreSQL.

## PostgreSQL

PostgreSQL contains:

- Silver layer for cleaned operational data
- Gold layer for analytical data
- Fact and Dimension tables
- Views and Materialized Views
- Stored Procedures
- Triggers

## Apache Kafka

Kafka provides real-time event streaming through seven topics.

The producer reads data from PostgreSQL and publishes it to Kafka.

The FastAPI Kafka consumer receives messages and stores the latest data in the in-memory `kafka_messages` dictionary.

## Apache Airflow

Airflow orchestrates Kafka producer execution.

event_pipeline
→ run_kafka_stream
→ airflow_producer.py
→ Kafka

## FastAPI Backend

Provides APIs for:

- Dashboard
- Crowd Intelligence
- Gate Monitoring
- Revenue
- Bookings
- Incidents
- Workflow Automation
- Kafka Stream

## React Frontend

The React dashboard includes:

- Event Command Center
- Crowd Intelligence
- Gate Monitoring
- Revenue Portal
- Emergency Center
- Workflow Automation
- Kafka Stream Monitor

## Power BI

Power BI provides analytical dashboards for revenue, ticketing, crowd monitoring, gate operations, incidents, and fan experience.

## Project Flow

CSV Data
→ ETL
→ PostgreSQL
→ Kafka
→ FastAPI
→ React

PostgreSQL
→ Power BI

Airflow
→ Kafka Producer Automation

## Key Features

- ETL data processing
- PostgreSQL Silver and Gold layers
- Real-time Kafka streaming
- Airflow orchestration
- FastAPI REST APIs
- React monitoring dashboard
- Workflow automation
- Power BI analytics
