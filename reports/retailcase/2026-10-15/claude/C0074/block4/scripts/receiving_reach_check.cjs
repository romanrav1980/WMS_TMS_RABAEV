// C0074 блок 4: старший приёмки и ТСД водителя ричтрака (живой API, только чтение).
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const BASE = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html?workspace=";
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async () => {
  const b = await chromium.launch(); const res = { writes: [], errors: [] };
  const open = async (role, viewport, ready) => {
    const p = await (await b.newContext({ viewport })).newPage();
    p.on("request", r => { if (r.method() !== "GET" && r.url().includes("/api/")) res.writes.push(r.method() + " " + r.url()); });
    p.on("pageerror", e => res.errors.push(role + ": " + String(e)));
    await p.goto(BASE + role); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass);
    await p.click("button[type=submit]"); await p.waitForSelector(ready, { timeout: 30000 }); await p.waitForTimeout(3500); return p;
  };
  const r = await open("receiving", { width: 1600, height: 1100 }, ".ops-kpi");
  res.receiving = { kpis: (await r.locator(".ops-kpi").allInnerTexts()).map(t => t.replace(/\s+/g, " ")), note: await r.locator(".rg-window .ops-note").innerText() };
  const tok = r.locator("g[role=button][aria-label^='Поставка']").first();
  await tok.focus(); await r.keyboard.press("Enter"); await r.waitForSelector(".ops-right dl", { timeout: 15000 });
  res.receiving.card = (await r.locator(".ops-right .ops-card").innerText()).replace(/\s+/g, " ").slice(0, 600);
  await r.screenshot({ path: `${OUT}/r1_receiving.png` });
  await r.locator(".rg-window input").fill("31217707"); await r.waitForTimeout(800);
  res.receiving.filtered = (await r.locator(".ops-kpi").allInnerTexts()).map(t => t.replace(/\s+/g, " "));
  const t = await open("reach", { width: 420, height: 900 }, ".ops-device");
  res.reach = (await t.locator(".ops-device").innerText()).replace(/\s+/g, " ").slice(0, 400);
  res.reachOverflow = await t.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  await t.screenshot({ path: `${OUT}/r2_reach_tsd.png`, fullPage: true });
  const m = await open("receiving", { width: 390, height: 844 }, ".ops-kpi");
  res.mobileOverflow = await m.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  await m.screenshot({ path: `${OUT}/r3_receiving_mobile.png`, fullPage: true });
  fs.writeFileSync(`${OUT}/../receiving_reach_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
