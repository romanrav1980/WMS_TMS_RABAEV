// C0074 блок 3: хранение/ричтраки, двор и ворота, общий Гант на столах директора и диспетчера (живой API, только чтение).
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const BASE = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html?workspace=";
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async () => {
  const b = await chromium.launch(); const res = { writes: [], errors: [] };
  const open = async (role, viewport = { width: 1600, height: 1100 }, pickWh = false) => {
    const p = await (await b.newContext({ viewport })).newPage();
    p.on("request", r => { if (r.method() !== "GET" && r.url().includes("/api/")) res.writes.push(r.method() + " " + r.url()); });
    p.on("pageerror", e => res.errors.push(role + ": " + String(e)));
    await p.goto(BASE + role); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass);
    await p.click("button[type=submit]");
    if (pickWh) { await p.waitForSelector(".rg-window input", { timeout: 30000 }); res.needsWarehouse = res.needsWarehouse ?? await p.locator(".ops").innerText().then(t => t.includes("первый не подставляется")); await p.locator(".rg-window input").first().fill("1"); }
    await p.waitForSelector(".ops-kpi", { timeout: 30000 }); await p.waitForTimeout(4000); return p;
  };
  const s = await open("storage", undefined, true);
  res.storage = { kpis: (await s.locator(".ops-kpi").allInnerTexts()).map(t => t.replace(/\s+/g, " ")), list: (await s.locator(".ops-right").innerText()).replace(/\s+/g, " ").slice(0, 300) };
  const tok = s.locator("g[role=button][aria-label^='Задание']").first();
  if (await tok.count()) { await tok.focus(); await s.keyboard.press("Enter"); await s.waitForTimeout(2000); res.storage.card = (await s.locator(".ops-right .ops-card").innerText()).replace(/\s+/g, " ").slice(0, 600); }
  await s.screenshot({ path: `${OUT}/t1_storage.png` });
  const y = await open("yard");
  res.yard = { kpis: (await y.locator(".ops-kpi").allInnerTexts()).map(t => t.replace(/\s+/g, " ")), gap: await y.locator("[data-help-id='workspace.yard.gap']").innerText() };
  await y.getByLabel("Склад/РЦ").fill("1"); await y.waitForSelector(".rg-summary", { timeout: 30000 });
  res.yard.gantt = await y.locator(".rg-summary").innerText(); res.yard.typesOn = await y.locator(".rg-seg button[aria-pressed=true]").allInnerTexts();
  await y.screenshot({ path: `${OUT}/t2_yard.png`, fullPage: true });
  const d = await open("director");
  res.director = { ganttSection: await d.locator("[aria-label='Общий Гант ресурсов']").count() };
  await d.screenshot({ path: `${OUT}/t3_director_with_gantt.png`, fullPage: true });
  const m = await open("storage", { width: 390, height: 844 }, true);
  res.mobileOverflow = await m.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  await m.screenshot({ path: `${OUT}/t4_storage_mobile.png`, fullPage: true });
  fs.writeFileSync(`${OUT}/../desks_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
