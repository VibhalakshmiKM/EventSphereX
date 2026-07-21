from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://postgres:vibha22@localhost:5432/eventspherex"
)

try:
    conn = engine.connect()
    print("Connected Successfully")
    conn.close()
except Exception as e:
    print(e)