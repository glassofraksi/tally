import { getDatabase } from "@netlify/database";

export default async () => {
  try {
    const db = getDatabase();
    const rows = await db.sql`SELECT upload_date, status FROM uploads`;
    const result = {};
    for (const r of rows) {
      const d = r.upload_date instanceof Date
        ? r.upload_date.toISOString().slice(0, 10)
        : String(r.upload_date).slice(0, 10);
      result[d] = r.status;
    }
    return Response.json(result);
  } catch (e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
};

export const config = {
  path: "/.netlify/functions/get_calendar",
};
