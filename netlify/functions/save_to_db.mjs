import { getDatabase } from "@netlify/database";

export default async (req) => {
  try {
    const body = await req.json().catch(() => ({}));
    const rows = Array.isArray(body.rows) ? body.rows : [];
    const uploadDate = body.date || new Date().toISOString().slice(0, 10);

    const db = getDatabase();
    const client = await db.pool.connect();

    try {
      await client.query("BEGIN");

      for (const row of rows) {
        const ticker = String(row.ticker ?? "").trim().toUpperCase();
        if (!ticker) continue;

        const newVals = [
          Number(row.pct_change_current_quarter),
          Number(row.pct_change_next_quarter),
          Number(row.pct_change_current_fiscal_year),
          Math.trunc(Number(row.num_current_fiscal_year_estimates)),
        ];

        const existing = await client.query(
          `SELECT pct_change_current_quarter,
                  pct_change_next_quarter,
                  pct_change_current_fiscal_year,
                  num_current_fiscal_year_estimates,
                  count
             FROM tickers
            WHERE ticker = $1`,
          [ticker]
        );

        if (existing.rowCount === 0) {
          await client.query(
            `INSERT INTO tickers (
               ticker, date,
               pct_change_current_quarter,
               pct_change_next_quarter,
               pct_change_current_fiscal_year,
               num_current_fiscal_year_estimates,
               count
             ) VALUES ($1, $2, $3, $4, $5, $6, 1)`,
            [ticker, uploadDate, ...newVals]
          );
        } else {
          const e = existing.rows[0];
          const oldVals = [
            Number(e.pct_change_current_quarter),
            Number(e.pct_change_next_quarter),
            Number(e.pct_change_current_fiscal_year),
            Number(e.num_current_fiscal_year_estimates),
          ];
          const oldCount = Number(e.count);

          let increases = 0;
          let decreases = 0;
          for (let i = 0; i < 4; i++) {
            if (newVals[i] > oldVals[i]) increases++;
            else if (newVals[i] < oldVals[i]) decreases++;
          }
          const newCount = decreases === 0 && increases >= 2 ? oldCount + 1 : oldCount;

          await client.query(
            `UPDATE tickers
                SET date = $1,
                    pct_change_current_quarter = $2,
                    pct_change_next_quarter = $3,
                    pct_change_current_fiscal_year = $4,
                    num_current_fiscal_year_estimates = $5,
                    count = $6
              WHERE ticker = $7`,
            [uploadDate, ...newVals, newCount, ticker]
          );
        }
      }

      await client.query(
        `INSERT INTO uploads (upload_date, status)
         VALUES ($1, 'success')
         ON CONFLICT (upload_date)
         DO UPDATE SET status = EXCLUDED.status`,
        [uploadDate]
      );

      await client.query("COMMIT");
    } catch (err) {
      await client.query("ROLLBACK");
      throw err;
    } finally {
      client.release();
    }

    return Response.json({ message: "Saved successfully" });
  } catch (e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
};

export const config = {
  path: "/.netlify/functions/save_to_db",
};
