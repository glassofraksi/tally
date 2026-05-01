import json
import pandas as pd
import io
import base64

def is_valid_number(val):
    try:
        float(val)
        return True
    except:
        return False

def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        csv_b64 = body.get("file")
        if not csv_b64:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing file"})}

        csv_data = base64.b64decode(csv_b64).decode("utf-8", errors="ignore")
        df = pd.read_csv(io.StringIO(csv_data))

        df = df.drop(columns=["Company"], errors="ignore")
        expected = [
            "Ticker",
            "%Ch Curr Qtr Est - 4 wks",
            "%Ch Next Qtr  Est - 4 wks",
            "%Ch Curr Fiscal Yr Est - 4 wks",
            "# Up Curr Fiscal Yr Est - 4 wks"
        ]
        df = df[[c for c in expected if c in df.columns]]

        cleaned = []
        for _, row in df.iterrows():
            ticker = str(row.get("Ticker", "")).strip()
            if not ticker or ticker.lower() == "nan" or ticker.lower() == "average":
                continue

            vals = [
                row.get("%Ch Curr Qtr Est - 4 wks"),
                row.get("%Ch Next Qtr  Est - 4 wks"),
                row.get("%Ch Curr Fiscal Yr Est - 4 wks"),
                row.get("# Up Curr Fiscal Yr Est - 4 wks")
            ]

            if not all(is_valid_number(v) for v in vals):
                continue

            cleaned.append({
                "ticker": ticker,
                "pct_change_current_quarter": float(vals[0]),
                "pct_change_next_quarter": float(vals[1]),
                "pct_change_current_fiscal_year": float(vals[2]),
                "num_current_fiscal_year_estimates": int(float(vals[3]))
            })

        return {"statusCode": 200, "body": json.dumps({"preview": cleaned})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
