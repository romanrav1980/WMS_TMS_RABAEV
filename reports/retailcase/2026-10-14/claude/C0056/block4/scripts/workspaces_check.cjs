// C0056 блок 4: рабочие места в стиле цифрового двойника на реальном API (только чтение; команды не отправляются).
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const URL0 = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html";
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async () => {
  const b = await chromium.launch(); const res = { posts: [] };
  const open = async (viewport, query = "") => {
    const p = await (await b.newContext({ viewport })).newPage();
    p.on("request", r => { if (r.method() !== "GET" && r.url().includes("/api/")) res.posts.push(r.method() + " " + r.url()); });
    await p.goto(URL0 + query); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass);
    await p.click("button[type=submit]"); await p.waitForSelector(".ops", { timeout: 30000 }); return p;
  };
  const p = await open({ width: 1600, height: 1000 }, "?workspace=director");
  await p.fill("input[type=date]", "2026-10-14"); await p.waitForTimeout(3500);
  res.director = { kpis: (await p.locator(".ops-kpi").allInnerTexts()).map(t => t.replace(/\s+/g, " ")),
    processes: (await p.locator(".ops-proc button").allInnerTexts()).map(t => t.replace(/\s+/g, " ")),
    trucks: await p.locator(".ops-truck").count(), ganttBars: await p.locator(".ops-gantt-track button").count(), sessions: await p.locator(".ops-bottom .ops-list li").count() };
  await p.screenshot({ path: `${OUT}/w1_director_desktop.png` });
  if (res.director.trucks) { await p.locator(".ops-truck").first().click(); await p.waitForSelector(".ops-card", { timeout: 5000 });
    res.director.card = (await p.locator(".ops-card").innerText()).replace(/\s+/g, " ").slice(0, 400); }
  if (res.director.ganttBars) { await p.locator(".ops-gantt-track button").first().click(); res.director.cardFromGantt = (await p.locator(".ops-card h3").innerText()).replace(/\s+/g, " "); }
  await p.locator(".ops-truck").first().focus(); await p.keyboard.press("Enter"); res.director.keyboardCard = await p.locator(".ops-card").count();
  await p.screenshot({ path: `${OUT}/w2_director_card.png` });
  res.director.sources = (await p.locator(".ops-sources").innerText()).replace(/\s+/g, " ");
  res.director.dispatchButton = await p.locator(".ops-card").getByRole("button", { name: /Открыть рейс/ }).innerText();
  await p.locator(".ops-proc button", { hasText: "Волны" }).click(); await p.waitForSelector(".ops-right .ops-card", { timeout: 5000 });
  res.director.wavesList = (await p.locator(".ops-right .ops-card h3").innerText()).replace(/\s+/g, " ");
  res.director.wavesOwner = await p.locator(".ops-right .ops-card").getByRole("button", { name: "Панель смены", exact: true }).count();
  res.director.wavesTitle = await p.locator(".ops-proc button", { hasText: "Волны" }).getAttribute("title");
  await p.screenshot({ path: `${OUT}/w2b_director_process_list.png` });
  await p.locator(".ops-proc button", { hasText: "Отгружено" }).click(); await p.waitForTimeout(300);
  res.director.filterTitle = await p.locator(".ops-scene-title").innerText();
  await p.getByRole("tab", { name: "Диспетчер", exact: true }).click(); await p.waitForTimeout(3000);
  res.dispatcher = { kpis: (await p.locator(".ops-kpi").allInnerTexts()).map(t => t.replace(/\s+/g, " ")), processes: (await p.locator(".ops-proc button").allInnerTexts()).map(t => t.replace(/\s+/g, " ")) };
  await p.locator(".ops-proc button", { hasText: "Без водителя" }).click(); await p.waitForTimeout(300);
  res.dispatcher.filterTitle = await p.locator(".ops-scene-title").innerText();
  await p.screenshot({ path: `${OUT}/w3_dispatcher_desktop.png` });
  const t = await open({ width: 420, height: 900 }, "?workspace=picker"); await t.waitForTimeout(3500);
  res.picker = (await t.locator(".ops-device").innerText()).replace(/\s+/g, " ").slice(0, 500);
  res.pickerOverflow = await t.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  await t.screenshot({ path: `${OUT}/w4_picker_tsd.png`, fullPage: true });
  const d = await open({ width: 390, height: 844 }, "?workspace=driver"); await d.waitForTimeout(1500);
  res.driver = (await d.locator(".ops-device").innerText()).replace(/\s+/g, " ").slice(0, 200);
  await d.screenshot({ path: `${OUT}/w5_driver_login.png` });
  const m = await open({ width: 390, height: 844 }, "?workspace=director"); await m.fill("input[type=date]", "2026-10-14"); await m.waitForTimeout(3000);
  res.mobileOverflow = await m.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  await m.screenshot({ path: `${OUT}/w6_director_mobile.png`, fullPage: true });
  fs.writeFileSync(`${OUT}/../c0056_block4_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
