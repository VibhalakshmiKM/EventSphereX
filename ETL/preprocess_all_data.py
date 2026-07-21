import pandas as pd
import os

# Input files
files = {
    "ticket_booking_data.csv": ["Booking_Time"],
    "payment_transactions.csv": ["Timestamp"],
    "crowd_movement_tracking.csv": ["Entry_Time", "Exit_Time"],
    "entry_gate_scans.csv": ["Scan_Time"],
    "food_merchandise_sales.csv": ["Timestamp"],
    "event_app_activity_logs.csv": ["Timestamp"],
    "emergency_incident_logs.csv": ["Timestamp"]
}

input_folder = r"F:\EventSphereX\data"
output_folder = r"F:\EventSphereX\data\cleaned"

os.makedirs(output_folder, exist_ok=True)

for file_name, datetime_cols in files.items():

    print("\n" + "=" * 60)
    print(f"Processing: {file_name}")

    file_path = os.path.join(input_folder, file_name)

    df = pd.read_csv(file_path)

    # Remove extra spaces from column names
    df.columns = df.columns.str.strip()

    # Standardize column names
    df.columns = df.columns.str.lower()

    # Convert datetime columns
    for col in datetime_cols:
        col = col.lower()
        df[col] = pd.to_datetime(df[col])

    # Verify duplicates
    print("\nDuplicate Rows:")
    print(df.duplicated().sum())

    # Verify missing values
    print("\nMissing Values:")
    print(df.isnull().sum())

    # Data types
    print("\nData Types:")
    print(df.dtypes)

    # Save cleaned dataset
    output_file = os.path.join(
        output_folder,
        file_name.replace(".csv", "_clean.csv")
    )

    df.to_csv(output_file, index=False)

    print(f"\nSaved: {output_file}")

print("\nAll datasets processed successfully.")