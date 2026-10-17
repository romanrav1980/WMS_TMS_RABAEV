// C0074 блок 2: старший смены и общий Гант на реальном API (только чтение; POST/PATCH не отправляются).
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const WH = "6558233"; // склад с волной 478 (открытая задача размещения, нехватка запаса)
const URL0 = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html?workspace=shift";
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async () => {
  const b = await chromium.launch(); const res = { writes: [], errors: [] };
  const open = async viewport => {
    const p = await (await b.newContext({ viewport })).newPage();
    p.on("request", r => { if (r.method() === "GET" || !r.url().includes("/api/")) return;
      // shift-overview — read-only POST (C-0088), учитывается отдельно; остальное — изменяющие запросы.
      if (r.url().endsWith("/api/picking/shift-overview")) (res.overview = res.overview || []).push(r.postData()); else res.writes.push(r.method() + " " + r.url()); });
    p.on("pageerror", e => res.errors.push(String(e)));
    await p.goto(URL0); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass);
    await p.click("button[type=submit]"); await p.waitForSelector(".rg-window input", { timeout: 30000 });
    res.beforeWarehouse = res.beforeWarehouse ?? await p.locator(".ops").innerText().then(t => t.includes("первый не подставляется"));
    await p.locator(".rg-window input").first().fill(WH); await p.waitForSelector(".ops-kpi", { timeout: 30000 }); return p;
  };
  const p = await open({ width: 1600, height: 1100 });
  await p.waitForFunction(() => /[1-9]\d* из [1-9]\d* видимых волн(?! \(загрузка)/.test(document.querySelector('.ops-left .ops-note')?.textContent || ''), null, { timeout: 30000 });
  res.kpis = (await p.locator(".ops-kpi").allInnerTexts()).map(t => t.replace(/\s+/g, " "));
  res.stages = await p.locator("svg g[data-help-id^='shift.scene.stage'] > text").allInnerTexts();
  res.procNote = (await p.locator(".ops-left .ops-note").innerText()).replace(/\s+/g, " ");
  await p.screenshot({ path: `${OUT}/s1_shift_desktop.png` });
  await p.locator(".ops-proc button", { hasText: "Риски запуска" }).click(); await p.waitForTimeout(300);
  res.risks = (await p.locator(".ops-right .ops-list li").allInnerTexts()).slice(0, 6).map(t => t.replace(/\s+/g, " "));
  await p.screenshot({ path: `${OUT}/s2_shift_risks.png` });
  const firstWave = p.locator("g[role=button][aria-label^='Волна FULL.QA:628b79593a']").first();
  if (await firstWave.count()) { await firstWave.focus(); await p.keyboard.press("Enter"); await p.waitForTimeout(2500);
    res.waveCard = (await p.locator(".ops-right .ops-card").first().innerText()).replace(/\s+/g, " ").slice(0, 700); }
  await p.screenshot({ path: `${OUT}/s3_shift_wave_card.png` });
  await p.getByLabel(/Начало/).fill("2026-10-08T00:00"); await p.getByLabel("Часов").fill("168");
  await p.waitForSelector(".rg-summary", { timeout: 30000 }); await p.waitForTimeout(800);
  res.gantt = { summary: await p.locator(".rg-summary").innerText(), sources: await p.locator(".ops-sources").last().innerText(), rows: await p.locator(".rg-row:not(.rg-axis)").count(),
    queue: await p.locator(".rg-queue h4").innerText(), states: await p.locator(".rg-state").allInnerTexts() };
  const lbl = p.locator(".rg-label").nth(1); if (await lbl.count()) { await lbl.click(); res.gantt.card = (await p.locator(".ops-card").last().innerText()).replace(/\s+/g, " ").slice(0, 500); }
  await p.locator(".rg-planner").screenshot({ path: `${OUT}/s4_shift_gantt_live.png` });
  await p.locator(".rg-window input").first().fill("999999999"); await p.waitForTimeout(3000);
  res.foreignWarehouse = (await p.locator(".ops-err").allInnerTexts()).join(" | ").slice(0, 400);
  res.ganttHiddenForForeign = await p.locator(".rg-summary").count();
  await p.locator(".rg-window input").first().fill(WH); await p.waitForSelector(".rg-planner"); await p.getByLabel("Часов").fill("200"); await p.waitForTimeout(500);
  res.hoursClamped = await p.getByLabel("Часов").inputValue();
  const m = await open({ width: 390, height: 844 }); await m.waitForTimeout(5000);
  res.mobileOverflow = await m.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  await m.screenshot({ path: `${OUT}/s5_shift_mobile.png`, fullPage: true });
  fs.writeFileSync(`${OUT}/../shift_live_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
