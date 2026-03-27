import os
import psycopg2
from dotenv import load_dotenv
import time
load_dotenv() 

def get_connection():
    for i in range(5):
        try:
            return psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST", "db"),
                port=os.getenv("POSTGRES_PORT", "5432")
            )
        except Exception:
            print("DB not ready, retrying...")
            time.sleep(2)
    
    raise Exception("Cannot connect to DB")

