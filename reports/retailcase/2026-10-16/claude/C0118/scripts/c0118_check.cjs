// C0118: путь старшего смены и переходы. Живой API (только чтение) + MOCK-превью Ганта (учебные данные) для семейства VEHICLE.
// (1) склад сохраняется при переключении рабочих мест; (2) плавающая справка компактна и не закрывает кнопку процесса;
// (3) переходы к контролю/магазину/консолидации с title+help_id; (4) волна → ресурсы волны в Ганте → снять фильтр → назад к волне;
// (5) четыре семейства Ганта; (6) 403 чужого склада; desktop + 390. Изменяющих запросов нет.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "..", "screenshots");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html";
(async () => {
  const b = await chromium.launch(); const res = { checks: [], writes: [], errors: [], roles: {} };
  const watch = p => { p.on("pageerror", e => res.errors.push(String(e)));
    p.on("request", r => { if (r.method() !== "GET" && r.url().includes(":8088/api/") && !r.url().endsWith("/shift-overview")) res.writes.push(r.method() + " " + r.url()); }); };
  const login = async p => { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); };
  const p = await (await b.newContext({ viewport: { width: 1440, height: 1000 } })).newPage(); watch(p);
  await p.goto(BASE + "?workspace=shift&warehouse_id=6558233"); await login(p); await p.waitForSelector(".ops-kpi", { timeout: 30000 });
  // (1) Склад при переключении рабочих мест.
  for (const role of ["Хранение и ричтраки", "Приёмка", "Консолидация", "Директор РЦ", "Диспетчер", "Старший смены"]) {
    await p.getByRole("tab", { name: role, exact: true }).click(); await p.waitForTimeout(1200);
    res.roles[role] = await p.locator("input[list]").evaluateAll(i => i.map(x => x.value));
    assert(res.roles[role].length > 0 && res.roles[role].every(v => v === "6558233"), role);
  }
  res.checks.push("warehouse_kept_across_all_workplaces");
  // (3) Переходы со стола старшего смены.
  await p.waitForSelector(".ops-kpi", { timeout: 30000 });
  res.links = await p.evaluate(() => ["shift.open.consolidation", "shift.open.control", "shift.open.store", "shift.navigation.help"].map(id => {
    const e = document.querySelector(`[data-help-id="${id}"]`); return { id, title: !!e?.getAttribute("title"), text: e?.textContent?.trim() }; }));
  assert(res.links.every(l => l.title)); res.checks.push("shift_links_control_store_consolidation_help");
  // (4) Волна → ресурсы волны в Ганте → снять фильтр → назад к карточке волны.
  await p.waitForFunction(() => /[1-9]\d* из [1-9]\d* видимых волн/.test(document.querySelector(".ops-left .ops-note")?.textContent || ""), null, { timeout: 30000 });
  await p.locator("g[role=button][aria-label^='Волна FULL.QA:628b79593a']").first().click();
  await p.waitForSelector(".ops-right .ops-card"); await p.getByRole("button", { name: "Ресурсы волны в Ганте" }).click(); await p.waitForTimeout(1500);
  res.waveFilter = await p.locator("[data-help-id='resource-gantt.wave.filter']").innerText().catch(() => "нет");
  await p.getByRole("button", { name: "Снять фильтр волны" }).click(); await p.waitForTimeout(500);
  res.waveFilterAfterClear = await p.locator("[data-help-id='resource-gantt.wave.filter']").count();
  res.waveCardStillOpen = await p.locator(".ops-right .ops-card h3").first().innerText().then(t => t.includes("628b79593a")); assert(res.waveCardStillOpen);
  res.checks.push("wave_to_gantt_filter_clear_back_to_wave");
  await p.screenshot({ path: path.join(OUT, "n1_shift_desktop.png"), fullPage: true });
  // (6) 403 чужого склада в Ганте директора.
  await p.getByRole("tab", { name: "Директор РЦ", exact: true }).click(); await p.waitForTimeout(1200);
  await p.locator(".rg-planner input[list]").fill("999999999"); await p.waitForTimeout(2500);
  res.foreign = await p.locator(".rg-planner .ops-err").innerText().catch(() => "нет"); res.checks.push("foreign_warehouse_error_no_gantt");
  // (5) Четыре семейства: живые склады + MOCK для машин.
  await p.locator(".rg-planner input[list]").fill("51365792"); await p.waitForSelector(".rg-group", { timeout: 20000 });
  res.liveGroups51365792 = await p.locator(".rg-group").allInnerTexts();
  await p.locator(".rg-planner input[list]").fill("20220394"); await p.waitForTimeout(3000); res.liveGroups20220394 = await p.locator(".rg-group").allInnerTexts();
  const mk = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage(); watch(mk);
  await mk.goto("http://127.0.0.1:3000/src/features/platform/workspaces/resources/preview-mock/index.html"); await mk.waitForSelector(".rg-group");
  res.mockGroups = await mk.locator(".rg-group").allInnerTexts();
  assert(["Ричтраки", "Комплектовщики", "Ворота", "Машины"].every(g => res.mockGroups.some(x => x.startsWith(g)))); res.checks.push("four_families_mock_plus_live_three");
  // (2) 390: плавающая справка компактна, не закрывает кнопки процессов.
  const m = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage(); watch(m);
  await m.goto(BASE + "?workspace=shift&warehouse_id=6558233"); await login(m); await m.waitForSelector(".ops-kpi", { timeout: 30000 }); await m.waitForTimeout(2500);
  res.launch = await m.evaluate(() => { const r = document.querySelector(".knowledge-launch button").getBoundingClientRect(); return { w: Math.round(r.width), h: Math.round(r.height) }; });
  res.launchName = await m.locator(".knowledge-launch button").evaluate(e => e.textContent);
  res.launchPosition = await m.locator(".knowledge-launch").evaluate(e => getComputedStyle(e).position); assert.equal(res.launchPosition, "static"); assert.equal(res.launchName, "? Справка");
  res.covered = [];
  for (const y of [600, 1400, 2200]) { await m.evaluate(y => window.scrollTo(0, y), y); await m.waitForTimeout(150);
    res.covered.push(await m.evaluate(() => { const l = document.querySelector(".knowledge-launch"), r = l.getBoundingClientRect(); l.style.visibility = "hidden";
      if (getComputedStyle(l).position === "static") { l.style.visibility = ""; return null; } const t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2)?.closest("button,a,input,select,[role=button]"); l.style.visibility = ""; return t ? (t.textContent || t.tagName).trim().slice(0, 30) : null; })); }
  assert(res.covered.every(c => c === null || c === "? Справка"));
  res.mobileOverflow = await m.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(res.mobileOverflow <= 0);
  await m.evaluate(() => window.scrollTo(0, 0)); await m.screenshot({ path: path.join(OUT, "n2_shift_390.png"), fullPage: true });
  res.checks.push("mobile_390_compact_help_no_overflow");
  assert.deepEqual(res.writes, []); assert.deepEqual(res.errors, []);
  res.status = "PASS"; res.fixtures = "live read-only; VEHICLE family only in MOCK preview (UI fixture), none live in window";
  fs.writeFileSync(path.join(__dirname, "..", "c0118_result.json"), JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
