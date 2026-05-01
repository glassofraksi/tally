import { getDatabase } from "@netlify/database";

export default async () => {
  try {
    const db = getDatabase();
    const rows = await db.sql`
      SELECT ticker, date, pct_change_current_quarter,
             pct_change_next_quarter, pct_change_current_fiscal_year,
             num_current_fiscal_year_estimates, count
      FROM tickers
      ORDER BY count DESC, ticker ASC
    `;

    const result = rows.map((r) => {
      const d = r.date instanceof Date
        ? r.date.toISOString().slice(0, 10)
        : String(r.date).slice(0, 10);
      return {
        ticker: r.ticker,
        date: d,
        pct_change_current_quarter: Number(r.pct_change_current_quarter),
        pct_change_next_quarter: Number(r.pct_change_next_quarter),
        pct_change_current_fiscal_year: Number(r.pct_change_current_fiscal_year),
        num_current_fiscal_year_estimates: Number(r.num_current_fiscal_year_estimates),
        count: Number(r.count),
      };
    });

    return Response.json(result);
  } catch (e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
};

export const config = {
  path: "/.netlify/functions/get_tickers",
};
