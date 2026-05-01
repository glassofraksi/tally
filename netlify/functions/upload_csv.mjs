import { parse } from "csv-parse/sync";

const EXPECTED_COLUMNS = [
  "Ticker",
  "%Ch Curr Qtr Est - 4 wks",
  "%Ch Next Qtr  Est - 4 wks",
  "%Ch Curr Fiscal Yr Est - 4 wks",
  "# Up Curr Fiscal Yr Est - 4 wks",
];

const isValidNumber = (val) => {
  if (val === null || val === undefined || val === "") return false;
  const n = Number(String(val).trim());
  return Number.isFinite(n);
};

export default async (req) => {
  try {
    const body = await req.json().catch(() => ({}));
    const fileB64 = body.file;
    if (!fileB64) {
      return Response.json({ error: "Missing file" }, { status: 400 });
    }

    const csvText = Buffer.from(fileB64, "base64").toString("utf-8");

    const records = parse(csvText, {
      columns: true,
      skip_empty_lines: true,
      relax_column_count: true,
      trim: true,
    });

    const cleaned = [];
    for (const row of records) {
      const ticker = String(row.Ticker ?? "").trim();
      if (!ticker || ticker.toLowerCase() === "nan" || ticker.toLowerCase() === "average") {
        continue;
      }

      const vals = EXPECTED_COLUMNS.slice(1).map((col) => row[col]);
      if (!vals.every(isValidNumber)) continue;

      cleaned.push({
        ticker,
        pct_change_current_quarter: Number(vals[0]),
        pct_change_next_quarter: Number(vals[1]),
        pct_change_current_fiscal_year: Number(vals[2]),
        num_current_fiscal_year_estimates: Math.trunc(Number(vals[3])),
      });
    }

    return Response.json({ preview: cleaned });
  } catch (e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
};

export const config = {
  path: "/.netlify/functions/upload_csv",
};
