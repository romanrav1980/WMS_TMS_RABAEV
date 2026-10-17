// Только чтение: вид списка и редактора после правки CSS.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1440, height: 1000 } })).newPage(); const posts = [];
  p.on("request", r => { if (r.method() !== "GET" && r.url().includes("/api/")) posts.push(r.url()); });
  await p.goto("http://127.0.0.1:3000/src/features/platform/knowledge-editor/preview/index.html");
  await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  await p.waitForSelector(".ke-list li", { timeout: 30000 });
  await p.locator(".ke-list li", { hasText: "access-admin" }).getByRole("button", { name: "Открыть", exact: true }).click(); await p.waitForTimeout(1200);
  const buttonHeights = await p.locator(".ke-list li button").evaluateAll(n => n.map(x => Math.round(x.getBoundingClientRect().height)));
  await p.screenshot({ path: `${OUT}/k5_editor_desktop.png` });
  console.log(JSON.stringify({ buttonHeights, posts })); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
