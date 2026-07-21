import pandas as pd
files = [
    r"F:\EventSphereX\data\ticket_booking_data.csv",
    r"F:\EventSphereX\data\payment_transactions.csv",
    r"F:\EventSphereX\data\crowd_movement_tracking.csv",
    r"F:\EventSphereX\data\entry_gate_scans.csv",
    r"F:\EventSphereX\data\food_merchandise_sales.csv",
    r"F:\EventSphereX\data\event_app_activity_logs.csv",
    r"F:\EventSphereX\data\emergency_incident_logs.csv"
]

for file in files:
    print("\n" + "="*60)
    print(file)

    df = pd.read_csv(file)

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicates:")
    print(df.duplicated().sum())

    print("\nFirst 5 Rows:")
    print(df.head())