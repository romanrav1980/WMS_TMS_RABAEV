// C0124: KPI V2 на рабочем месте. (A) ЖИВОЕ чтение: вход admin, GET /api/resources/picker-kpis склада 20266481 (история CASE1152:
// 1 целая коробка + 1 штука + связанный возврат 25 EA). (B) UI FIXTURE (перехват того же GET): строка с согласованной недостачей,
// разные единицы, null = нет данных, общий возврат. Fixture — не серверная приёмка. Изменяющих запросов нет; пароль не печатается.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "..", "screenshots");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const live = JSON.parse(fs.readFileSync("C:/projects/TMS/reports/retailcase/2026-10-17/kpi-v2/api-live-v2.json", "utf8")).response;
const WH = "20266481", URL0 = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html?workspace=kpi&warehouse_id=" + WH
  + "&kpi_start=2026-10-15T04:00&kpi_finish=2026-10-17T05:00&kpi_zone=%2B00:00";
const res = { writes: [], errors: [], live: {}, fixture: {} };

function fixture() {
  const base = JSON.parse(JSON.stringify(live)); const op = base.operators[0];
  const shortOp = { ...JSON.parse(JSON.stringify(op)), operator_id: "FIXTURE.PICKER.B", completed_lines: 2, boxes: null, pieces: null,
    box_reasons: ["PACKAGING_PROOF_UNAVAILABLE"], shortage_completed_lines: 1,
    shortage_quantities: [{ article: "FX-A", base_uom: "EA", quantity: "3" }, { article: "FX-W", base_uom: "KG", quantity: "1.25" }],
    return_events: 2, returned_quantities: [{ article: "FX-A", base_uom: "EA", quantity: "2" }, { article: "FX-W", base_uom: "KG", quantity: "0.5" }],
    line_completions: [
      { operation_id: "FX.FULL.1", task_id: 9001, line_id: 1, actor: "FIXTURE.PICKER.B", at: "2026-10-16T08:10:00+00:00", approved_at: null, kind: "FULL", quantity: "10", shortage_quantity: "0" },
      { operation_id: "FX.SHORT.2", task_id: 9001, line_id: 2, actor: "FIXTURE.PICKER.B", at: "2026-10-16T08:20:00+00:00", approved_at: "2026-10-16T09:05:00+00:00", kind: "ACCEPTED_SHORT", quantity: "7", shortage_quantity: "3" }],
    observed_pick_coverage: { total: 3, covered_work: 3, covered_shift: 3, complete_for_observed_picks: true },
    rates: { lines_per_assembly_hour: "4", boxes_per_assembly_hour: null, lines_per_shift_hour: "2.5", boxes_per_shift_hour: null },
    registered_assembly_hours: "0.5", registered_shift_hours: "0.8", uncovered_work_operations: [], uncovered_shift_operations: [] };
  base.operators = [op, shortOp]; return base;
}

async function page(b, w, h, mode) {
  const p = await (await b.newContext({ viewport: { width: w, height: h } })).newPage();
  p.on("pageerror", e => res.errors.push(mode + w + ": " + e));
  p.on("request", r => { if (r.method() !== "GET" && r.url().includes(":8088/api/")) res.writes.push(r.method() + " " + r.url()); });
  if (mode === "fixture") await p.route(u => u.href.includes("/api/resources/picker-kpis"), r => r.request().method() === "OPTIONS" ? r.continue()
    : r.fulfill({ json: fixture(), headers: { "access-control-allow-origin": "http://127.0.0.1:3000", "access-control-allow-credentials": "true" } }));
  // Отчёт читается сам по параметрам адреса (kpi_start/kpi_finish/kpi_zone) сразу после входа.
  const reply = p.waitForResponse(r => r.url().includes("/api/resources/picker-kpis") && r.request().method() === "GET", { timeout: 40000 });
  await p.goto(URL0); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  res[mode]["status" + w] = (await reply).status();
  await p.waitForSelector("section[aria-label='Выработка комплектовщиков'] .kpi-metric", { timeout: 30000 });
  return p;
}

async function inspect(p, operatorId) {
  const sec = p.locator("section[aria-label='Выработка комплектовщиков']");
  await sec.locator("select[data-help-id='kpi.operator']").selectOption(operatorId);
  await sec.locator("summary[data-help-id='kpi.pick.details']").click();
  return sec.evaluate(s => ({
    note: s.querySelector(":scope > .ops-note")?.textContent,
    summary: s.querySelector(".kpi-summary")?.innerText,
    completions: [...s.querySelectorAll(".kpi-details table")][0]?.innerText.slice(0, 600),
    quality: s.querySelector(".kpi-quality")?.innerText ?? null,
    text: s.innerText,
    overflow: document.documentElement.scrollWidth - innerWidth,
  }));
}

(async () => {
  const b = await chromium.launch();
  for (const [w, h] of [[1440, 1000], [390, 844]]) {
    const p = await page(b, w, h, "live"); const r = await inspect(p, live.operators[0].operator_id);
    assert(/целых коробок: 1 · штук отдельно: 1/.test(r.summary), r.summary);
    assert(/Связанные возвраты по его строкам: 1 · AS16A410F14B915: 25 EA/.test(r.summary), r.summary);
    assert(/Отборы во времени: сборки — 0 из 2, смены — 0 из 2/.test(r.summary), r.summary);
    assert(/Полностью/.test(r.completions) && !/полного планового количества|ещё не согласованы|отдельного правила/.test(r.text));
    assert(r.overflow <= 0); res.live["w" + w] = { summary: r.summary, quality: r.quality, overflow: r.overflow };
    await p.locator(".kpi-summary").scrollIntoViewIfNeeded(); await p.screenshot({ path: path.join(OUT, `k1_live_${w}.png`) }); await p.context().close();
  }
  for (const [w, h] of [[1440, 1000], [390, 844]]) {
    const p = await page(b, w, h, "fixture"); const r = await inspect(p, "FIXTURE.PICKER.B");
    assert(/из них с согласованной недостачей: 1/.test(r.summary) && /целых коробок: Нет данных · штук отдельно: Нет данных/.test(r.summary), r.summary);
    assert(/С согласованной недостачей/.test(r.completions) && /Согласованная недостача\s*FX-A: 3 EA · FX-W: 1[.,]25 KG/.test(r.quality), r.quality);
    assert(/2 события · FX-A: 2 EA · FX-W: 0[.,]5 KG/.test(r.quality) && /не вина сотрудника/.test(r.summary), r.quality + r.summary);
    assert(/сборки — 3 из 3, смены — 3 из 3 · все наблюдённые отборы во времени/.test(r.summary));
    assert(r.overflow <= 0); res.fixture["w" + w] = { summary: r.summary, quality: r.quality, completions: r.completions, overflow: r.overflow };
    await p.locator(".kpi-quality").scrollIntoViewIfNeeded(); await p.screenshot({ path: path.join(OUT, `k2_fixture_${w}.png`) }); await p.context().close();
  }
  assert.deepEqual(res.writes, []); assert.deepEqual(res.errors, []); res.status = "PASS";
  res.labels = { live: "admin login + GET picker-kpis warehouse 20266481 (actual)", fixture: "intercepted picker-kpis GET (UI fixture, not acceptance)" };
  fs.writeFileSync(path.join(__dirname, "..", "kpi_v2_check.json"), JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e.message); console.error(JSON.stringify(res, null, 1).slice(0, 3000)); process.exit(1); });
