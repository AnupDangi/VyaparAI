import os
import psycopg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the connection string from the .env file
conn_string = os.getenv("DATABASE_URL")

try:
    with psycopg.connect(conn_string) as conn:
        print("Connection established")

        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute("SELECT NOW();")
            result = cur.fetchone()
            print("Database time:", result[0])

except Exception as e:
    print("Connection failed.")
    print(e)
