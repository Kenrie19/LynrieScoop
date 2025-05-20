import os
import time
import psycopg2
from psycopg2 import OperationalError

DB_HOST = os.environ.get("DB_HOST", "database")
DB_PORT = os.environ.get("DB_PORT", 5432)
DB_NAME = os.environ.get("DB_NAME", "cinema")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "postgres")

MAX_RETRIES = 20
WAIT_SECONDS = 2

if __name__ == "__main__":
    retries = 0
    while retries < MAX_RETRIES:
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                host=DB_HOST,
                port=DB_PORT
            )
            conn.close()
            print("Database is available!")
            break
        except OperationalError as e:
            print(f"Database not available yet: {e}")
            retries += 1
            time.sleep(WAIT_SECONDS)
    else:
        print("Could not connect to the database after several attempts.")
        exit(1)
