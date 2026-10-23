// Живые GET (и read-only POST shift-overview) для разведки источников C-0142. Пароль из AGENTS.md не печатается.
const fs = require("fs");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const H = { Authorization: "Basic " + Buffer.from("admin:" + pass).toString("base64") };
const API = "http://127.0.0.1:8088";
async function get(p, opt = {}) { const t = Date.now(); const r = await fetch(API + "/" + p.replace(/^[/]+/, ""), { headers: { ...H, ...(opt.headers || {}) }, ...opt }); const txt = await r.text(); let j; try { j = JSON.parse(txt); } catch { j = txt; }
  return { s: r.status, ms: Date.now() - t, j, rid: r.headers.get("x-request-id") }; }
(async () => {
  const out = {};
  for (const p of process.argv.slice(2)) { const r = await get(p); out[p] = r; console.log(r.s, r.ms + "ms", p, typeof r.j === "string" ? r.j.slice(0, 200) : JSON.stringify(r.j).slice(0, 600)); }
  fs.writeFileSync(__dirname + "/probe-last.json", JSON.stringify(out, null, 1));
})();
