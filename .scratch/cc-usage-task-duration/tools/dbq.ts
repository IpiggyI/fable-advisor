import { Database } from "bun:sqlite";
const db = new Database(process.argv[2]!, { readonly: true });
const ids = process.argv.slice(3);
for (const id of ids) {
  const rows = db.query(`SELECT agent, CASE WHEN agent='grok' THEN timestamp_ms - COALESCE(duration_ms,0) ELSE COALESCE(estimated_start_ms, timestamp_ms) END s, CASE WHEN agent='grok' THEN timestamp_ms ELSE COALESCE(estimated_end_ms, timestamp_ms) END e, CASE WHEN agent='grok' THEN duration_ms IS NULL ELSE estimated_start_ms IS NULL END u FROM usage_records WHERE session_id = ? ORDER BY s`).all(id) as any[];
  let active = 0, prevEnd = -Infinity, sum = 0, untimed = 0;
  for (const r of rows) { const s = r.s, e = Math.max(r.s, r.e); sum += e - s; untimed += r.u; active += Math.max(0, e - Math.max(s, prevEnd)); prevEnd = Math.max(prevEnd, e); }
  const span = rows.length ? (Math.max(...rows.map(r => r.e)) - rows[0].s) : 0;
  console.log(id.slice(0, 8), rows[0]?.agent, `calls=${rows.length} untimed=${untimed} active(union)=${(active / 60000).toFixed(1)}m sum=${(sum / 60000).toFixed(1)}m span=${(span / 60000).toFixed(1)}m`);
}
