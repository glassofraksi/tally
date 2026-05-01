import json
import os
import psycopg2

def handler(event, context):
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tickers (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(20) NOT NULL UNIQUE,
                date DATE NOT NULL,
                pct_change_current_quarter NUMERIC,
                pct_change_next_quarter NUMERIC,
                pct_change_current_fiscal_year NUMERIC,
                num_current_fiscal_year_estimates NUMERIC,
                count INTEGER DEFAULT 1
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id SERIAL PRIMARY KEY,
                upload_date DATE NOT NULL UNIQUE,
                status VARCHAR(20) DEFAULT 'success'
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        return {"statusCode": 200, "body": json.dumps({"message": "DB initialized"})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
