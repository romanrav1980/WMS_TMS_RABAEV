// C-0018: доступные СТ страницами по 200 в TransportDispatchPage. Только чтение (GET); назначений не выполняется.
// Ошибка API подставляется только в последнем сценарии, чтобы проверить отсутствие демоданных.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const PAGE_URL = "http://127.0.0.1:3000/?page=transport";
(async () => {
  const b = await chromium.launch(); const res = { requests: [], console: [] };
  const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 }, serviceWorkers: "block" }); const p = await ctx.newPage();
  const t0 = {};
  p.on("request", (r) => { if (r.url().includes("/available-sts")) { t0[r.url()] = Date.now(); } });
  p.on("response", (r) => { if (r.url().includes("/available-sts")) { const u = new URL(r.url()); res.requests.push({ query: Object.fromEntries(u.searchParams), status: r.status(), ms: Date.now() - (t0[r.url()] || Date.now()) }); } });
  p.on("console", (m) => { if (m.type() === "error" && !/ws\/dispatch/.test(m.text())) res.console.push(m.text().slice(0, 200)); });
  await p.goto(PAGE_URL); await p.waitForSelector(".st-pages", { timeout: 60000 });
  const bar = () => p.locator(".st-pages").first().innerText();
  const rows = () => p.locator(".dispatch-st-section tbody tr:not(.dispatch-virtual-spacer):not(:has(.dispatch-grid-empty))").count();
  await p.waitForFunction(() => /Загружено|не загружены|Сервер|Нет права/.test(document.querySelector(".st-pages")?.textContent || ""), null, { timeout: 90000 });
  res.initial = { bar: await bar() };
  // период шире, чтобы проверить следующую страницу на реальных данных
  // период шире, чтобы проверить следующую страницу: «Дата СТ» и «Дата до» из панели фильтров
  await p.locator("label.dispatch-tbl-label", { hasText: "Дата СТ" }).locator("input[type=date]").fill("2025-01-01");
  if (!(await p.locator("input.dispatch-fp-input[type=date]").isVisible())) await p.locator(".dispatch-fp-collapse-btn").click();
  await p.locator("input.dispatch-fp-input[type=date]").fill("2026-12-31"); res.dateInputs = 2;
  await p.waitForFunction(() => /Загружено \d+/.test(document.querySelector(".st-pages")?.textContent || "") && !/Загружаем/.test(document.querySelector(".st-pages")?.textContent || "") && /2025-01-01 — 2026-12-31/.test(document.querySelector(".st-pages")?.textContent || ""), null, { timeout: 180000 });
  res.wide = { bar: await bar() };
  await p.screenshot({ path: `${OUT}/s1_first_page_desktop.png` });
  if (/есть ещё/.test(res.wide.bar)) {
    await p.getByRole("button", { name: /Загрузить ещё/ }).click();
    await p.waitForFunction(() => /страниц 2/.test(document.querySelector(".st-pages")?.textContent || ""), null, { timeout: 120000 });
    res.secondPage = { bar: await bar() };
    await p.locator(".st-pages").first().screenshot({ path: `${OUT}/s2_second_page_bar.png` });
  }
  // выбор → смена фильтра склада: выбор не переживает неподходящий фильтр, страницы сбрасываются
  const firstBox = p.locator(".dispatch-st-section tbody tr input[type=checkbox]").first();
  if (await firstBox.count()) { await firstBox.check(); res.selectedBefore = await p.locator(".dispatch-st-section tbody tr input[type=checkbox]:checked").count(); }
  const ware = p.locator('[aria-label="Склад СТ"], [aria-label="Номер склада СТ"]').first();
  res.wareControl = await ware.evaluate((n) => n.tagName + ":" + n.getAttribute("aria-label"));
  if (res.wareControl.startsWith("SELECT")) { const opts = await ware.locator("option").evaluateAll((os) => os.map((o) => o.value).filter(Boolean)); res.wareOptions = opts.length; await ware.selectOption(opts.includes("9807") ? "9807" : opts[0]); }
  else { await ware.fill("9807"); await ware.press("Enter"); }
  await p.waitForFunction(() => !/Загружаем/.test(document.querySelector(".st-pages")?.textContent || ""), null, { timeout: 120000 });
  await p.waitForTimeout(500);
  res.afterWare = { bar: await bar(), selected: await p.locator(".dispatch-sel-bar").count() ? (await p.locator(".dispatch-sel-bar").innerText()).slice(0, 120) : "нет выделения" };
  // медленный прошлый ответ не перезаписывает текущий: задержать запрос склада 9807, быстро вернуть "все склады"
  await p.route(/available-sts.*ware_id=9807/, async (route) => { await new Promise((x) => setTimeout(x, 4000)); route.continue(); });
  if (res.wareControl.startsWith("SELECT")) { await ware.selectOption(""); await ware.selectOption("9807"); await ware.selectOption(""); }
  await p.waitForTimeout(6000);
  res.staleCheck = { bar: await bar(), lastRequests: res.requests.slice(-3).map((r) => r.query.ware_id || "все") };
  await p.unroute(/available-sts.*ware_id=9807/);
  // ошибка API: показывается ошибка и повтор, демоданных нет
  await p.route(/available-sts/, (route) => route.fulfill({ status: 500, headers: { "access-control-allow-origin": "*" }, body: '{"detail":"mock failure"}' }));
  await p.getByTitle("Обновить список СТ").click(); await p.waitForTimeout(1500);
  res.error = { bar: await bar(), rows: await rows(), demo: await p.getByText("ул. Ленина 5").count(), empty: await p.locator(".dispatch-st-section .dispatch-grid-empty").count() ? await p.locator(".dispatch-st-section .dispatch-grid-empty").innerText() : "" };
  await p.screenshot({ path: `${OUT}/s3_error_retry.png` });
  await p.unroute(/available-sts/); await p.getByRole("button", { name: "Повторить" }).click();
  await p.waitForFunction(() => /Загружено/.test(document.querySelector(".st-pages")?.textContent || ""), null, { timeout: 120000 });
  res.afterRetry = { bar: await bar() };
  fs.writeFileSync(`${OUT}/../c0018_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
