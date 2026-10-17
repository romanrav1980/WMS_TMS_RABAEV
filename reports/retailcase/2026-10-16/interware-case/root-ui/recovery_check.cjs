// C0117: обзор восстановления недостач у старшего смены. Живой API: пустая выборка склада 20220394 и 403 чужого склада.
// UI FIXTURES (перехват /api/inventory/recovery-shorts в браузере, не native): этапы, предел 50, 5xx → устаревший снимок,
// смена склада без показа прежней выборки, переход «недостача → волна 478 → назад». Изменяющих запросов нет.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "screenshots");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html?workspace=shift";
const WH = 6558233;
const row = (i, status, state, extra = {}) => ({ short_id: 9000 + i, case_pick_task_id: 2000 + i, case_pick_line_id: 3000 + i, pick_wave_id: 478, warehouse_id: WH,
  inventory_task_id: null, replenish_task_id: null, warehouse_task_id: null, status, recovery_state: state, cell: "FIX-CELL-" + i, article: "FIX-ART-" + i, picker: "fixture",
  inventory_status: null, auditor: null, count_operation_id: null, replenish_status: null, wait_reason: null, recovery_last_error: null,
  short_quantity: "3", restored_quantity: "0", order_remaining_quantity: "3", age_seconds: 120, remaining_seconds: 180, recovery_deadline_at: "2026-10-16T15:20:00", restored_at: null, ...extra });
const STAGED = [row(1, "PENDING_APPROVAL", null), row(2, "APPROVED", "WAIT_INVENTORY", { inventory_task_id: 77, inventory_status: "ASSIGNED", auditor: "auditor1" }),
  row(3, "APPROVED", "WAIT_REPLENISHMENT", { replenish_task_id: 88, replenish_status: "WAITING", wait_reason: "NO_SOURCE_STOCK", warehouse_task_id: 564 }),
  row(4, "APPROVED", "READY", { restored_quantity: "3", restored_at: "2026-10-16T15:10:00" }), row(5, "APPROVED", "FAILED", { recovery_last_error: "SOURCE_CELL_LOCKED", remaining_seconds: -240 }),
  row(6, "APPROVED", "NEW_SERVER_STATE")];
(async () => {
  const b = await chromium.launch(); const res = { checks: [], writes: [], errors: [] };
  const p = await (await b.newContext({ viewport: { width: 1500, height: 1100 } })).newPage();
  p.on("pageerror", e => res.errors.push(String(e)));
  p.on("request", r => { if (r.method() !== "GET" && r.url().includes(":8088/api/") && !r.url().endsWith("/shift-overview")) res.writes.push(r.method() + " " + r.url()); });
  const recovery = () => p.getByRole("button", { name: /Восстановление недостач/ });
  // Процесс открыт — повторное нажатие его свернёт; нажимаем, только если панели ещё нет.
  const ensureRecovery = async () => { await p.waitForTimeout(400); if (!(await p.locator(".rc").count())) await recovery().click(); };
  await p.goto(BASE + "&warehouse_id=20220394"); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  await p.waitForSelector(".ops-kpi", { timeout: 30000 }); await recovery().click(); await p.waitForTimeout(2500);
  res.liveEmpty = (await p.locator(".rc").innerText()).replace(/\s+/g, " ").slice(0, 200); assert(res.liveEmpty.includes("Открытых недостач в выборке нет")); res.checks.push("live_empty_selected_warehouse");
  // Живой 403: чужой/недоступный склад.
  await p.locator(".rg-window input[list]").first().fill("999999999"); await p.waitForTimeout(3000); await ensureRecovery(); await p.waitForTimeout(2000);
  res.live403 = (await p.locator(".rc").innerText()).replace(/\s+/g, " ").slice(0, 220); assert(res.live403.includes("Нет права")); assert(!res.live403.includes("Открытых недостач")); res.checks.push("live_403_hides_data");
  // FIXTURES.
  const fx = { mode: "ok", rows: STAGED };
  await p.route("**/api/inventory/recovery-shorts*", async r => {
    const ware = new URL(r.request().url()).searchParams.get("ware_id");
    if (fx.mode === "500") return r.fulfill({ status: 503, json: { detail: "fixture unavailable" } });
    if (ware === "20220394") { await new Promise(x => setTimeout(x, 2500)); return r.fulfill({ status: 200, json: [] }); }
    return r.fulfill({ status: 200, json: fx.rows });
  });
  await p.locator(".rg-window input[list]").first().fill(String(WH)); await p.waitForSelector(".ops-kpi", { timeout: 30000 }); await ensureRecovery();
  await p.waitForSelector(".rc-row"); res.stages = await p.locator(".rc-stages button").allInnerTexts();
  assert.deepEqual(res.stages.length, 6); res.unknownRow = await p.locator(".rc-row", { hasText: "FIX-ART-6" }).innerText(); assert(res.unknownRow.includes("NEW_SERVER_STATE") && res.unknownRow.includes("Неизвестное состояние")); res.checks.push("fixture_six_stages_unknown_marked");
  await p.screenshot({ path: path.join(OUT, "r1_recovery_desktop.png"), fullPage: true });
  await p.locator(".rc-stages button", { hasText: "Пополнение" }).click(); res.filtered = await p.locator(".rc-row").count(); assert.equal(res.filtered, 1);
  await p.locator(".rc-row").first().click(); res.card = (await p.locator(".rc-card").innerText()).replace(/\s+/g, " ").slice(0, 600);
  res.links = await p.locator(".rc-card a").evaluateAll(a => a.map(x => x.getAttribute("href").replace(/^https?:\/\/[^/]+/, "")));
  assert(res.links.some(l => l === "/wms-admin/short-investigation.html?short_id=9003")); assert(res.links.some(l => l === "/wms-admin/warehouse-tasks.html?task_id=564"));
  assert(res.links.some(l => l === "/wms-admin/wave-replenishment.html?wave_id=478&ware_id=6558233")); res.checks.push("card_links_existing_screens_only");
  res.sceneSelected = await p.locator("g[role=button][aria-pressed=true]").count();
  await p.getByRole("button", { name: "Волна", exact: true }).click(); await p.waitForTimeout(1500);
  res.waveCard = await p.locator(".ops-right .ops-card h3").first().innerText(); assert(res.waveCard.includes("628b79593a"));
  await p.locator(".ops-right").getByRole("button", { name: "Закрыть карточку" }).first().click(); await p.waitForTimeout(500);
  res.backToSame = await p.locator(".rc-card").innerText().then(t => t.includes("9003")); assert(res.backToSame); res.checks.push("wave_and_back_to_same_short");
  // 50 строк — «полнота неизвестна».
  fx.rows = Array.from({ length: 50 }, (_, i) => row(100 + i, "PENDING_APPROVAL", null));
  await p.getByRole("button", { name: "← К списку" }).click(); await p.locator(".rc").getByRole("button", { name: "Обновить" }).click(); await p.waitForTimeout(1500);
  res.limitNote = await p.locator(".rc .ops-note").first().innerText(); assert(res.limitNote.includes("полнота неизвестна")); res.checks.push("fifty_rows_completeness_unknown");
  // 5xx: прежний снимок остаётся только с пометкой «устарел».
  fx.mode = "500"; await p.locator(".rc").getByRole("button", { name: "Обновить" }).click(); await p.waitForTimeout(1500);
  res.staleText = await p.locator(".rc .ops-err").innerText(); assert(res.staleText.includes("устарел")); fx.mode = "ok"; res.checks.push("5xx_stale_marked");
  // Смена склада: прежняя выборка не показывается, пока читается новый склад.
  await p.locator(".rg-window input[list]").first().fill("20220394"); await p.waitForTimeout(600); await ensureRecovery(); await p.waitForTimeout(300);
  res.duringSwitch = await p.locator(".rc-row").count(); assert.equal(res.duringSwitch, 0); await p.waitForTimeout(3000);
  res.afterSwitch = (await p.locator(".rc").innerText()).replace(/\s+/g, " ").slice(0, 120); res.checks.push("warehouse_switch_no_previous_sample");
  // Mobile 390.
  const m = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage();
  await m.route("**/api/inventory/recovery-shorts*", r => r.fulfill({ status: 200, json: STAGED }));
  await m.goto(BASE + "&warehouse_id=" + WH); await m.fill("input[autocomplete=username]", "admin"); await m.fill("input[type=password]", pass); await m.click("button[type=submit]");
  await m.waitForSelector(".ops-kpi", { timeout: 30000 }); await m.getByRole("button", { name: /Восстановление недостач/ }).click(); await m.waitForSelector(".rc-row");
  await m.locator(".rc-row").nth(2).click(); res.mobileOverflow = await m.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(res.mobileOverflow <= 0);
  await m.locator(".rc-card").scrollIntoViewIfNeeded(); await m.screenshot({ path: path.join(OUT, "r2_recovery_card_390.png"), fullPage: true }); res.checks.push("mobile_390_card_back");
  assert.deepEqual(res.writes, []); assert.deepEqual(res.errors, []);
  res.status = "PASS"; res.fixtures = "live: empty + 403; positive states = UI fixtures (intercepted), not native";
  fs.writeFileSync(path.join(__dirname, "recovery_result.json"), JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
