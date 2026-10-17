// C0074 приёмка UI общего Ганта: старый ответ, потеря ответа, 403, перезагрузка, смена даты. Только чтение; сбои — через перехват маршрута в браузере.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const URL0 = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html?workspace=director"; // у директора свой выбор склада Ганта
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const A = "6667491", B = "51365792"; // A: 1 ресурс, B: 4 ресурса (живые данные 15.10)
(async () => {
  const b = await chromium.launch(); const res = { writes: [], errors: [] };
  const ctx = await b.newContext({ viewport: { width: 1500, height: 1000 } }); const p = await ctx.newPage();
  p.on("request", r => { if (r.method() !== "GET" && r.url().includes("/api/")) res.writes.push(r.method() + " " + r.url()); });
  p.on("pageerror", e => res.errors.push(String(e)));
  await p.goto(URL0); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  await p.waitForSelector(".rg-planner"); const wh = p.locator(".rg-planner .rg-window input[list]");
  const summary = async () => (await p.locator(".rg").count()) ? `склад ${await p.locator(".rg").getAttribute("data-warehouse")} · ${(await p.locator(".rg-summary").innerText()).split(" · ")[0]}` : "нет Ганта";
  // 1. Старый ответ: ответ по A задержан, пользователь уже выбрал B — на экране только B.
  await p.route(`**/api/resources/timeline?warehouse_id=${A}*`, async r => { await new Promise(x => setTimeout(x, 4000)); await r.continue(); });
  await wh.fill(A); await p.waitForTimeout(300); await wh.fill(B); await p.waitForTimeout(6000);
  res.staleResponse = { shown: await summary(), expected: "склад " + B };
  await p.unroute(`**/api/resources/timeline?warehouse_id=${A}*`);
  // 2. Потеря ответа: соединение оборвано — ошибка, Гант этого окна не выдумывается; «Обновить» перечитывает.
  await p.route("**/api/resources/timeline*", r => r.abort("connectionreset"));
  await wh.fill(A); await p.waitForTimeout(2000);
  res.lostResponse = { error: await p.locator(".rg-planner .ops-err").innerText().catch(() => "нет"), gantt: await summary() };
  await p.unroute("**/api/resources/timeline*");
  await p.getByRole("button", { name: "Обновить", exact: true }).click(); await p.waitForTimeout(6000);
  res.afterRefresh = await summary();
  // 3. 403 по складу: «нет права», Гант не показывается как пустой.
  await p.route("**/api/resources/timeline*", r => r.fulfill({ status: 403, contentType: "application/json", body: JSON.stringify({ detail: { code: "RESOURCE_TIMELINE_ACCESS_DENIED" } }) }));
  await wh.fill(B); await p.waitForTimeout(2000);
  res.forbidden = { error: await p.locator(".rg-planner .ops-err").innerText().catch(() => "нет"), gantt: await summary() };
  await p.unroute("**/api/resources/timeline*");
  // 4. Неизвестная форма ответа — ошибка, а не пустой Гант.
  await p.route("**/api/resources/timeline*", r => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ warehouse_id: Number(A), resources: [] }) }));
  await wh.fill(A); await p.waitForTimeout(2000);
  res.badShape = { error: await p.locator(".rg-planner .ops-err").innerText().catch(() => "нет"), gantt: await summary() };
  await p.unroute("**/api/resources/timeline*");
  // 5. Смена даты в шапке переводит интервал Ганта (если не задан свой).
  await wh.fill(B); await p.waitForTimeout(3000);
  await p.locator("header input[type=date]").fill("2026-10-10"); await p.waitForTimeout(3000);
  res.dayChange = { start: await p.getByLabel(/Начало/).inputValue(), gantt: await summary() };
  await p.getByLabel("Часов").fill("48"); await p.locator("header input[type=date]").fill("2026-10-12"); await p.waitForTimeout(1500);
  res.customInterval = { start: await p.getByLabel(/Начало/).inputValue(), note: await p.locator(".rg-window").innerText().then(t => t.includes("свой интервал")) };
  // 6. Перезагрузка страницы: роль из URL сохраняется, данные читаются заново, без ошибок.
  await p.reload(); await p.waitForTimeout(1500);
  res.reloadNeedsLogin = await p.locator("input[type=password]").count() > 0;
  if (res.reloadNeedsLogin) { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); }
  await p.waitForSelector(".ops-kpi", { timeout: 30000 });
  res.reload = { role: await p.locator("[role=tab][aria-selected=true]").first().innerText() };
  await p.screenshot({ path: `${OUT}/a1_after_reload.png` });
  fs.writeFileSync(`${OUT}/../acceptance_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
