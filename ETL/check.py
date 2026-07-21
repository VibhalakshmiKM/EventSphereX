import pandas as pd

df = pd.read_csv(
    
    r"F:\EventSphereX\data\cleaned\payment_transactions_clean.csv"
    
)
print(df.head())
print(df.dtypes)