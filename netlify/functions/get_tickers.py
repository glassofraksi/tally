import json
import os
import psycopg2

def handler(event, context):
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()
        cur.execute("""
            SELECT ticker, date, pct_change_current_quarter,
                   pct_change_next_quarter, pct_change_current_fiscal_year,
                   num_current_fiscal_year_estimates, count
            FROM tickers
            ORDER BY count DESC, ticker ASC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        result = []
        for r in rows:
            result.append({
                "ticker": r[0],
                "date": str(r[1]),
                "pct_change_current_quarter": float(r[2]),
                "pct_change_next_quarter": float(r[3]),
                "pct_change_current_fiscal_year": float(r[4]),
                "num_current_fiscal_year_estimates": int(r[5]),
                "count": int(r[6])
            })

        return {"statusCode": 200, "body": json.dumps(result)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
