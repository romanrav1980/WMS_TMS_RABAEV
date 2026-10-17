// Только чтение: вкладка назначений после исправления отображения времени без пояса.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage(); const posts = [];
  p.on("request", r => { if (r.method() !== "GET" && r.url().includes("/api/")) posts.push(r.url()); });
  await p.goto("http://127.0.0.1:3000/src/features/platform/access-admin/preview/index.html");
  await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  await p.waitForSelector(".aa-meta b", { timeout: 30000 });
  await p.getByRole("button", { name: "Показать", exact: true }).click(); await p.waitForTimeout(1500);
  const row = (await p.locator("tr", { hasText: "UI.C0056" }).first().innerText()).replace(/\s+/g, " ");
  await p.screenshot({ path: `${OUT}/a3_assignments_desktop.png`, fullPage: true });
  const m = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage();
  await m.goto("http://127.0.0.1:3000/src/features/platform/access-admin/preview/index.html");
  await m.fill("input[autocomplete=username]", "admin"); await m.fill("input[type=password]", pass); await m.click("button[type=submit]");
  await m.waitForSelector(".aa-meta b", { timeout: 30000 }); await m.locator(".help-hint-trigger").first().click();
  const top = await m.evaluate(() => { const r = document.querySelector(".help-hint-panel").getBoundingClientRect(); const el = document.elementFromPoint(r.left + 20, r.bottom - 20); return !!el && !!el.closest(".help-hint-panel"); });
  const overflow = await m.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  await m.screenshot({ path: `${OUT}/a4_mobile.png` });
  console.log(JSON.stringify({ row, posts, mobile: { hintOnTop: top, overflow } })); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
