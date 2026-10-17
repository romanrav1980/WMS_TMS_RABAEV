// C0074: (1) аудит справки на MOCK-Ганте (много полос/очередь); (2) все статьи, на которые ссылаются help_id рабочих мест, опубликованы.
const fs = require("fs"), path = require("path");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const ROOT = "C:/projects/TMS/admin/wms_admin_frontend/src/features/platform/workspaces";
const walk = d => fs.readdirSync(d, { withFileTypes: true }).flatMap(e => e.isDirectory() ? walk(path.join(d, e.name)) : /\.tsx?$/.test(e.name) ? [path.join(d, e.name)] : []);
(async () => {
  const res = {};
  const src = walk(ROOT).map(f => fs.readFileSync(f, "utf8")).join("\n");
  const articles = new Set([...src.matchAll(/article: "([a-z0-9-]+)"/g), ...src.matchAll(/\): HelpEntry => \(\{ id: [^,]+, text, article: "([a-z0-9-]+)"/g), ...src.matchAll(/text: string, article = "([a-z0-9-]+)"/g),
    ...src.matchAll(/, "([a-z0-9-]+)"\),\n/g)].map(m => m[1]));
  const auth = "Basic " + Buffer.from("admin:" + pass).toString("base64");
  res.articles = {};
  for (const a of articles) { const r = await fetch(`http://127.0.0.1:8088/api/help/articles/${a}`, { headers: { Authorization: auth } }); res.articles[a] = r.status; }
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1600, height: 1000 } })).newPage();
  await p.goto("http://127.0.0.1:3000/src/features/platform/workspaces/resources/preview-mock/index.html"); await p.waitForSelector(".rg-bar");
  res.mock = await p.evaluate(() => {
    const els = [...document.querySelectorAll(".ops button, .ops input, .ops select")];
    const bad = els.filter(e => { const near = e.closest("label, [role=group], .help-action"); const group = e.closest("[role=group]");
      const id = e.getAttribute("data-help-id") || near?.getAttribute("data-help-id") || near?.querySelector("[data-help-id]")?.getAttribute("data-help-id") || group?.getAttribute("data-help-id");
      const d = e.getAttribute("aria-describedby"); const tip = e.getAttribute("title") || (d && document.getElementById(d)?.textContent) || near?.getAttribute("title");
      return !id || !tip; }).map(e => (e.textContent || e.type).trim().slice(0, 30));
    return { total: els.length, bars: document.querySelectorAll(".rg-bar").length, missing: bad };
  });
  await b.close();
  fs.writeFileSync(path.join(process.argv[2], "../help_audit_mock_articles.json"), JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1));
})().catch(e => { console.error(e); process.exit(1); });
