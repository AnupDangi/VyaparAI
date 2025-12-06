import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the connection string from the .env file
conn_string = os.getenv("DATABASE_URL")

if not conn_string:
    raise RuntimeError(
        "DATABASE_URL is missing. Add it to a .env file (postgresql://.../... ?sslmode=require)."
    )

def get_db_connection():
    try:
        conn = psycopg.connect(conn_string, row_factory=dict_row, autocommit=True)
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise e

if __name__ == "__main__":
    try:
        with get_db_connection() as conn:
            print("Connection established")
            with conn.cursor() as cur:
                cur.execute("SELECT NOW();")
                result = cur.fetchone()
                print("Database time:", result['now'])
    except Exception as e:
        print("Connection failed.")
        print(e)
