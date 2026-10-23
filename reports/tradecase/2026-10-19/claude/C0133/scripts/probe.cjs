// C0133: живые GET под admin (только чтение) — форма ответов TRADECASE T02 склада 225837931. Пароль не печатается.
const fs = require("fs");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const H = { Authorization: "Basic " + Buffer.from("admin:" + pass).toString("base64") };
const W = "/api/tradecase/warehouses/225837931";
(async () => {
  const paths = [W + "/site", ...["SUPPLY", "SKU", "OWNER"].map(k => W + "/documents/" + k + "?limit=2"), W + "/stock/pallets?limit=5", "/api/access/workspaces?capability=tradecase"];
  for (const p of paths) {
    const t0 = Date.now();
    try {
      const r = await fetch("http://127.0.0.1:8088" + p, { headers: H, signal: AbortSignal.timeout(20000) });
      const t = await r.text();
      console.log(r.status, Date.now() - t0 + "ms", p, "\n ", p.endsWith("workspaces") ? t.slice(0, 300) : t.slice(0, 900));
    } catch (e) { console.log("ERR", Date.now() - t0 + "ms", p, String(e)); }
  }
})();
