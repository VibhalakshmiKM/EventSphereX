from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="event_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    run_kafka_stream = BashOperator(
        task_id="run_kafka_stream",
        bash_command="python /opt/airflow/dags/airflow_producer.py"
    )