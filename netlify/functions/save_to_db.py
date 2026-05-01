import json
import os
import psycopg2
from datetime import date

def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        rows = body.get("rows", [])
        upload_date = body.get("date") or str(date.today())

        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()

        for row in rows:
            ticker = row["ticker"].strip().upper()
            new_vals = [
                float(row["pct_change_current_quarter"]),
                float(row["pct_change_next_quarter"]),
                float(row["pct_change_current_fiscal_year"]),
                int(row["num_current_fiscal_year_estimates"])
            ]

            cur.execute("""
                SELECT pct_change_current_quarter,
                       pct_change_next_quarter,
                       pct_change_current_fiscal_year,
                       num_current_fiscal_year_estimates,
                       count
                FROM tickers
                WHERE ticker = %s
            """, (ticker,))
            existing = cur.fetchone()

            if existing is None:
                cur.execute("""
                    INSERT INTO tickers (
                        ticker, date,
                        pct_change_current_quarter,
                        pct_change_next_quarter,
                        pct_change_current_fiscal_year,
                        num_current_fiscal_year_estimates,
                        count
                    ) VALUES (%s, %s, %s, %s, %s, %s, 1)
                """, (ticker, upload_date, *new_vals))
            else:
                old_vals = [float(existing[0]), float(existing[1]), float(existing[2]), int(existing[3])]
                old_count = int(existing[4])
                increases = sum(1 for o, n in zip(old_vals, new_vals) if n > o)
                decreases = sum(1 for o, n in zip(old_vals, new_vals) if n < o)
                new_count = old_count + 1 if decreases == 0 and increases >= 2 else old_count

                cur.execute("""
                    UPDATE tickers
                    SET date = %s,
                        pct_change_current_quarter = %s,
                        pct_change_next_quarter = %s,
                        pct_change_current_fiscal_year = %s,
                        num_current_fiscal_year_estimates = %s,
                        count = %s
                    WHERE ticker = %s
                """, (upload_date, *new_vals, new_count, ticker))

        cur.execute("""
            INSERT INTO uploads (upload_date, status)
            VALUES (%s, 'success')
            ON CONFLICT (upload_date)
            DO UPDATE SET status = EXCLUDED.status
        """, (upload_date,))

        conn.commit()
        cur.close()
        conn.close()
        return {"statusCode": 200, "body": json.dumps({"message": "Saved successfully"})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
