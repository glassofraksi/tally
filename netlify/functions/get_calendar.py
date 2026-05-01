import json
import os
import psycopg2

def handler(event, context):
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()
        cur.execute("SELECT upload_date, status FROM uploads")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        result = {str(r[0]): r[1] for r in rows}
        return {"statusCode": 200, "body": json.dumps(result)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
