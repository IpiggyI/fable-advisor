import { Database } from "bun:sqlite";
const [db_, labf, ...ids] = process.argv.slice(2);
const db = new Database(db_!, { readonly: true });
const { t0, lab } = JSON.parse(await Bun.file(labf!).text());
const cov = new Uint8Array(lab.length);
for (const id of ids) {
  const rows = db.query(`SELECT agent, CASE WHEN agent='grok' THEN timestamp_ms - COALESCE(duration_ms,0) ELSE COALESCE(estimated_start_ms, timestamp_ms) END s, CASE WHEN agent='grok' THEN timestamp_ms ELSE COALESCE(estimated_end_ms, timestamp_ms) END e FROM usage_records WHERE session_id = ?`).all(id) as any[];
  for (const r of rows) for (let x = Math.floor(r.s / 1000 - t0); x < Math.ceil(r.e / 1000 - t0); x++) if (x >= 0 && x < cov.length) cov[x] = 1;
}
const agg: Record<string, [number, number]> = {};
lab.forEach((l: string, i: number) => { (agg[l] ??= [0, 0])[cov[i]]++; });
let c = 0; cov.forEach(v => c += v);
console.log(`wall=${(lab.length / 60).toFixed(0)}m  recorded-call coverage=${(c / 60).toFixed(0)}m (${(100 * c / lab.length).toFixed(0)}%)`);
console.log("label                     uncovered  covered");
for (const [k, [u, v]] of Object.entries(agg).sort((a, b) => b[1][0] - a[1][0])) if (u + v > 60) console.log(k.padEnd(26), (u / 60).toFixed(1).padStart(7) + "m", (v / 60).toFixed(1).padStart(7) + "m");
