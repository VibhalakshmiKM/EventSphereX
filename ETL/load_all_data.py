import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://postgres:vibha22@localhost:5432/eventspherex"
)

files = {
    "ticket_booking_data_clean.csv": "ticket_booking",
    "payment_transactions_clean.csv": "payment_transactions",
    "crowd_movement_tracking_clean.csv": "crowd_tracking",
    "entry_gate_scans_clean.csv": "entry_gate_scans",
    "food_merchandise_sales_clean.csv": "food_sales",
    "event_app_activity_logs_clean.csv": "event_app_logs",
    "emergency_incident_logs_clean.csv": "incident_logs"
}

for file_name, table_name in files.items():

    path = rf"F:\EventSphereX\data\cleaned\{file_name}"

    print(f"Loading {file_name}...")

    df = pd.read_csv(path)

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False
    )

    print(f"Loaded into {table_name}")

print("All datasets loaded successfully.")