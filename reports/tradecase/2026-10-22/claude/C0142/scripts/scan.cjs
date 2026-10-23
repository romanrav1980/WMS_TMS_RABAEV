// Разведка: какие склады дают какие виды ресурсов/событий в timeline (живые GET). Пароль не печатается.
const fs = require("fs");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const H = { Authorization: "Basic " + Buffer.from("admin:" + pass).toString("base64") };
const API = "http://127.0.0.1:8088/";
const g = async p => { const t = Date.now(); const r = await fetch(API + p, { headers: H }); return { s: r.status, ms: Date.now() - t, j: await r.json().catch(() => null) }; };
(async () => {
  const ws = (await g("api/access/workspaces")).j;
  const ids = ws.warehouses.filter(w => w.capabilities.resource_timeline).map(w => w.warehouse_id);
  console.log("timeline warehouses", ids.length, "has_more", ws.has_more, "limit", ws.limit);
  const from = process.argv[2] || "2026-10-15T00:00:00%2B03:00", to = process.argv[3] || "2026-10-22T00:00:00%2B03:00";
  const summary = [];
  for (const id of ids) {
    const r = await g(`api/resources/timeline?warehouse_id=${id}&start_at=${from}&finish_at=${to}`);
    if (r.s !== 200) { summary.push({ id, s: r.s, ms: r.ms, code: r.j?.detail?.code ?? r.j?.detail }); continue; }
    const t = r.j, rk = {}, ek = {}, av = {}; for (const x of t.resources) { rk[x.kind] = (rk[x.kind] || 0) + 1; av[x.availability] = (av[x.availability] || 0) + 1; }
    for (const e of [...t.events, ...t.unscheduled]) ek[e.kind] = (ek[e.kind] || 0) + 1;
    const m = {}; for (const a of t.assignments) m[a.event_id] = (m[a.event_id] || 0) + 1;
    if (t.resources.length || t.events.length) summary.push({ id, ms: r.ms, tz: t.warehouse_time_zone, rk, av, ek, unsched: t.unscheduled.length, multi: Object.values(m).filter(n => n > 1).length, overlaps: t.overlap_candidates.length,
      bad: t.sources.filter(s => s.status !== "READY").map(s => s.source_id + ":" + s.status) });
  }
  console.log(JSON.stringify(summary, null, 0).replace(/\},\{/g, "},\n{"));
  fs.writeFileSync(__dirname + "/scan-last.json", JSON.stringify(summary, null, 1));
})();
