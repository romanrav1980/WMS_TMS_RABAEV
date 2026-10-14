// C-0021: адресная проверка правок C-0018. Ответы /available-sts подставляются только здесь; назначений нет.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const st = (n, addr, ware) => ({ ST_NUMBER: n, ADDR: addr, WARE_ID: ware, REGION: "Тест", PALLETS_COUNT: 1, WEIGHT_KG: 10, VOLUME_M3: 0.1, STDATE: "2026-10-14", VERIFY_PERC: 100, RAION: null, TRANSPORT_TYPE: null, TRANSTASK_ID: null, NAPR: null });
const ALL = [st("ST-DUP", "Адрес A", 9807), st("ST-DUP", "Адрес B", 9807), st("ST-DUP", "Адрес A", 9201), st("ST-ONE", "Адрес C", 9807)];
const NEXT = [st("ST-NEW", "Адрес N", 9201)];
(async () => {
  const b = await chromium.launch(); const res = {};
  const p = await (await b.newContext({ viewport: { width: 1600, height: 1000 }, serviceWorkers: "block" })).newPage();
  let delayNext = false;
  await p.route(/available-sts/, async (route) => {
    const u = new URL(route.request().url()); const filtered = u.searchParams.get("addr_mask");
    if (filtered && delayNext) await new Promise((x) => setTimeout(x, 4000));
    route.fulfill({ status: 200, headers: { "access-control-allow-origin": "*", "content-type": "application/json" }, body: JSON.stringify(filtered ? NEXT : ALL) });
  });
  await p.goto("http://127.0.0.1:3000/?page=transport");
  await p.waitForFunction(() => /Загружено 4 СТ/.test(document.querySelector(".st-pages")?.textContent || ""), null, { timeout: 60000 });
  const rowTexts = () => p.locator(".dispatch-st-section tbody tr:not(.dispatch-virtual-spacer)").evaluateAll((rs) => rs.map((r) => r.innerText.replace(/\s+/g, " ").slice(0, 90)));
  res.dedup = { bar: await p.locator(".st-pages").innerText(), rows: await rowTexts() };
  // выбрать строку, затем сменить фильтр адреса с задержанным ответом
  await p.locator(".dispatch-st-section tbody tr input[type=checkbox]").first().check();
  res.selectedBefore = await p.locator(".dispatch-st-section tbody tr input[type=checkbox]:checked").count();
  delayNext = true;
  if (!(await p.locator(".dispatch-fp-input, input[placeholder*='Адрес']").first().isVisible())) await p.locator(".dispatch-fp-collapse-btn").click();
  await p.locator("input[placeholder*='Адрес']").first().fill("Адрес N");
  await p.waitForFunction(() => /Загружаем/.test(document.querySelector(".st-pages")?.textContent || "") || /Загружаем/.test(document.querySelector(".dispatch-st-section")?.textContent || ""), null, { timeout: 15000 });
  res.duringSwitch = { rows: await rowTexts(), checked: await p.locator(".dispatch-st-section tbody tr input[type=checkbox]:checked").count(), selBar: await p.locator(".dispatch-sel-bar").count(),
    addDisabled: await p.locator(".dispatch-sel-bar-add, .dispatch-add-btn").evaluateAll((bs) => bs.map((x) => x.disabled)) };
  await p.screenshot({ path: `${OUT}/s4_filter_switch_cleared.png` });
  await p.waitForFunction(() => /Загружено 1 СТ/.test(document.querySelector(".st-pages")?.textContent || ""), null, { timeout: 20000 });
  res.afterSwitch = { bar: await p.locator(".st-pages").innerText(), rows: await rowTexts(), checked: await p.locator(".dispatch-st-section tbody tr input[type=checkbox]:checked").count() };
  fs.writeFileSync(`${OUT}/../c0021_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
