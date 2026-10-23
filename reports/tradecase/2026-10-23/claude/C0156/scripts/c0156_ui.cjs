// C-0156 «Сборка коробов CASE на бумаге» (dev :3021) при 1440 и 390.
// ЖИВОЕ (только GET): вход, склады, очередь CASE склада 6667491 (/api/case-pick/tasks).
// FIXTURE TRANSPORT: /api/case-pick/tasks/{id}/paper — ответ собран из живых строк заданий 1019/1020 (case_paper_fixture_live.py; подпись —
// NOT_APPLIED line_signature как анонимный блок), т.к. API :8088 не перезапущен и пакет не применён. Изменённые версии → 409 (synthetic).
// FIXTURE: все POST подтверждения строки (503/403/ack/409) и 403 очереди. Живых записей нет: любой не-GET вне fixture прерывается и фиксируется.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const PAPER = JSON.parse(fs.readFileSync(path.join(OUT, "case-paper-fixture.json"), "utf8"));
const BASE = process.env.C0156_BASE || "http://127.0.0.1:3021/", WH = "6667491", T = 1019, L = PAPER["1019"].lines[0];
const CUR = L.reference, STALE = CUR.replace(/:[A-F0-9]{64}$/, ":" + "B".repeat(64));
const res = { base: BASE, checks: [], liveWrites: [], errors: [], posts: [], timings: {} };
let fx = {};
const cors = { "access-control-allow-origin": "*" };

async function route(r) {
  const req = r.request(), m = req.method(), u = new URL(req.url());
  if (m === "OPTIONS") return r.continue();
  const paper = /\/api\/case-pick\/tasks\/(\d+)\/paper$/.exec(u.pathname);
  if (paper && m === "GET") {
    const p = PAPER[paper[1]]; if (!p) return r.fulfill({ status: 404, json: { detail: { code: "CASE_TASK_NOT_FOUND" } }, headers: cors });
    const sig = u.searchParams.get("expected_signature"), line = u.searchParams.get("line");
    const delay = fx.delayStale && sig !== L.signature ? fx.delayStale : 0; if (delay) await new Promise(ok => setTimeout(ok, delay));
    if (sig && sig !== p.lines.find(x => String(x.line_id) === line)?.signature) return r.fulfill({ status: 409, json: { detail: { code: "CASE_PAPER_LINE_CHANGED" } }, headers: cors });
    const body = fx.device ? { ...p, lines: p.lines.map(x => ({ ...x, device_required: fx.device })) } : p;
    return r.fulfill({ status: 200, json: line ? { ...body, lines: body.lines.filter(x => String(x.line_id) === line) } : body, headers: cors });
  }
  if (m === "POST" && /\/api\/case-pick\/tasks\/\d+\/lines\/\d+\/confirm$/.test(u.pathname)) {
    const body = req.postData(); res.posts.push(body); const op = JSON.parse(body).operation_id, next = (fx.confirm || []).shift() || "ack";
    if (next === "ack") return r.fulfill({ status: 200, json: { operation_id: op, case_pick_task_id: T, case_pick_line_id: L.line_id, status: "PARTIAL" }, headers: cors });
    if (next === "503") return r.fulfill({ status: 503, json: { detail: { code: "RESULT_UNCERTAIN", operation_id: op, outcome_confirmed: false, retry_same_operation_id: true } }, headers: cors });
    if (next === "403") return r.fulfill({ status: 403, json: { detail: { code: "CASE_CURRENT_EXECUTE_REQUIRED", operation_id: op, outcome_confirmed: false, read_before_retry: true } }, headers: cors });
    if (next === "stale") return r.fulfill({ status: 409, json: { detail: { code: "STOCK_RULE_REJECTED", rule_reason: "ORA-20886: CASE_PAPER_LINE_CHANGED", operation_id: op, outcome_confirmed: true } }, headers: cors });
    if (next === "conflict") return r.fulfill({ status: 409, json: { detail: { code: "OPERATION_CONTENT_CONFLICT", operation_id: op, outcome_confirmed: true } }, headers: cors });
  }
  if (m === "GET" && /\/marking-policy$/.test(u.pathname)) return r.fulfill({ status: 200, json: { article: L.articul, marking_required: true, profiles: [{ system_code: "CRPT", profile_code: "WATER" }], serialized_weight_boxes: false, loose_weight_kg: false }, headers: cors });
  if (m !== "GET") { res.liveWrites.push(m + " " + u.href); return r.abort(); }
  if (fx.queue403 && /\/api\/case-pick\/tasks$/.test(u.pathname)) return r.fulfill({ status: 403, json: { detail: { code: "CASE_CURRENT_WARE_VIEWER_REQUIRED" } }, headers: cors });
  return r.continue();
}
const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };
const desk = p => p.locator("[aria-label='Бумажная сборка CASE']");

async function open(p, w) {
  await p.goto(`${BASE}?page=workspace&workspace=paper&warehouse_id=${WH}`);
  const login = p.locator("input[type=password]");
  await Promise.race([login.waitFor({ timeout: 30000 }), p.locator("[aria-label='Бумажные задания']").waitFor({ timeout: 30000 })]);
  if (await login.count()) { await p.fill("input[autocomplete=username]", "admin"); await login.fill(pass); await p.click("button[type=submit]"); }
  await p.getByRole("button", { name: "Сборка коробов CASE" }).click();
  await desk(p).locator("li").first().waitFor({ timeout: 30000 });
}
async function scan(p, code) {
  const f = desk(p).locator(".case-scan"); await f.getByLabel("Штрихкод строки с бланка CASE").fill(code); await f.getByRole("button", { name: "Сверить строку" }).click();
}
async function fill(p) {
  const f = desk(p).locator(".case-fact");
  await f.getByLabel("Скан ячейки").fill(L.cell_code); await f.getByLabel("Скан короба (SSCC)").fill(PAPER["1019"].task.sscc);
  await f.getByLabel("Скан товара").fill("4600000000000"); await f.getByLabel("Собрано всего по строке").fill("5");
  await f.getByRole("button", { name: "Внести факт" }).click();
}
const fact = p => desk(p).locator(".case-fact");

async function width(b, w, h) {
  fx = {};
  const ctx = await b.newContext({ viewport: { width: w, height: h } });
  await ctx.addInitScript(() => { window.print = () => { document.documentElement.dataset.printed = "1"; }; });
  const p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await ctx.route(u => u.href.includes(":8088/api/"), route);
  const t0 = Date.now(); await open(p, w); res.timings["case_queue_" + w] = Date.now() - t0;
  const text = await desk(p).innerText(); assert(text.includes("CASE 1019") && text.includes("CASE 1020")); ok(w, "LIVE CASE queue of warehouse 6667491: open tasks 1019/1020 listed");
  const bad = await p.locator(".paper-mode button, [aria-label='Бумажная сборка CASE'] button").evaluateAll(bs => bs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every button has title and help id");

  const row = desk(p).locator("li", { hasText: "CASE 1019" });
  await row.getByRole("button", { name: "Бланк" }).click(); await row.locator(".case-paper table").waitFor();
  assert((await row.innerText()).includes(L.cell_code)); ok(w, "FIXTURE-TRANSPORT paper of task 1019 (live rows) shows cell, plan, picked");
  const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(over <= 1, "overflow " + over); ok(w, "no horizontal page scroll");
  await desk(p).screenshot({ path: path.join(SHOTS, `case-paper-queue-${w}.png`) });
  const [popup] = await Promise.all([ctx.waitForEvent("page"), row.getByRole("button", { name: "Печать / PDF" }).click()]);
  await popup.waitForLoadState(); await popup.emulateMedia({ media: "print" });
  const probe = await popup.evaluate(() => { const s = document.querySelector("svg").getBoundingClientRect(); return { printed: document.documentElement.dataset.printed === "1",
    svgRight: Math.round(s.right), svgWidth: Math.round(s.width), viewport: innerWidth, scroll: document.documentElement.scrollWidth, code: document.querySelector("code").textContent, sections: document.querySelectorAll("section").length }; });
  res["print_" + w] = probe; assert(probe.printed && probe.code === CUR && probe.sections === 1 && probe.svgRight <= probe.viewport + 1 && probe.scroll <= probe.viewport + 1, JSON.stringify(probe));
  ok(w, "print sheet: one section per open line, CPICK barcode inside the page, print dialog requested");
  await popup.screenshot({ path: path.join(SHOTS, `case-paper-print-${w}.png`), fullPage: true });
  if (w === 1440) { await popup.pdf({ path: path.join(OUT, "case-paper-print.pdf"), preferCSSPageSize: true }); ok(w, "PDF rendered with the sheet's own page size"); }
  await popup.close();

  await scan(p, "WTASK:1019:" + L.signature); await desk(p).getByText("Считайте штрихкод строки").waitFor(); ok(w, "WTASK code is not accepted as CPICK");
  await scan(p, STALE); await desk(p).getByText("изменилась после печати").waitFor(); assert(await fact(p).count() === 0); ok(w, "stale sheet (synthetic 409) opens no fact entry");
  fx.delayStale = 1500; await scan(p, STALE); await p.waitForTimeout(100); await scan(p, CUR);
  await desk(p).getByText("актуален").waitFor(); await p.waitForTimeout(1800);
  const late = { stale: await desk(p).getByText("изменилась после печати").count(), where: await desk(p).getByText("изменилась после печати").allInnerTexts(), fact: await fact(p).count() }; assert(late.stale === 0 && late.fact === 1, JSON.stringify(late)); fx.delayStale = 0; ok(w, "late answer of the older check does not overwrite the newer one");

  fx.confirm = ["503"]; res.posts = []; await fill(p);
  await fact(p).getByText("Исход не подтверждён").waitFor(); await fact(p).getByRole("button", { name: "Повторить отправку" }).waitFor(); ok(w, "FIXTURE 503: fact kept with its operation id, retry offered");
  await open(p, w); await scan(p, CUR);  // full reload of the page (login again if the shell asks)
  await fact(p).getByRole("button", { name: "Повторить отправку" }).waitFor(); ok(w, "pending fact survives reload");
  fx.confirm = ["403"]; await fact(p).getByRole("button", { name: "Повторить отправку" }).click(); await fact(p).getByText("Доступ закрыт").waitFor();
  assert(await fact(p).getByRole("button", { name: "Повторить отправку" }).count() === 1); ok(w, "FIXTURE revoked access (403): fact kept, no new effect claimed");
  fx.confirm = ["ack"]; await fact(p).getByRole("button", { name: "Повторить отправку" }).click(); await fact(p).getByText("Факт строки принят").waitFor();
  assert(res.posts.length === 3 && new Set(res.posts).size === 1, JSON.stringify(res.posts)); const sent = JSON.parse(res.posts[0]);
  assert(sent.expected_case_signature === L.signature && sent.scan_container === PAPER["1019"].task.sscc && sent.fact_qty === "5" && /^case-paper-/.test(sent.operation_id));
  ok(w, "exact replay: three sends of identical bytes (same operation id, sheet version, scans); own receipt clears the fact");

  fx.confirm = ["stale"]; await fill(p); await fact(p).getByText("Бланк устарел").waitFor();
  assert(await fact(p).getByRole("button", { name: "Внести факт" }).count() === 1); ok(w, "FIXTURE native refusal CASE_PAPER_LINE_CHANGED is confirmed and shown");
  fx.confirm = ["conflict"]; await fill(p); await fact(p).getByText("OPERATION_CONTENT_CONFLICT").waitFor(); ok(w, "FIXTURE conflict is confirmed and shown");
  await fact(p).screenshot({ path: path.join(SHOTS, `case-paper-fact-${w}.png`) });

  fx.device = "MARKING_SCAN_REQUIRED"; await scan(p, CUR);
  const codeBox = fact(p).getByLabel("Код маркировки (сканер, Enter после каждого)"); await codeBox.waitFor();
  for (const c of ["0104600000000001215abcDEF", "0104600000000001215ghiJKL", "0104600000000001215abcDEF"]) { await codeBox.fill(c); await codeBox.press("Enter"); }
  await fact(p).getByText("Отсканировано кодов: 2").waitFor(); assert(await fact(p).getByLabel("Скан товара").count() === 0);
  fx.confirm = ["ack"]; res.posts = [];
  await fact(p).getByLabel("Скан ячейки").fill(L.cell_code); await fact(p).getByLabel("Скан короба (SSCC)").fill(PAPER["1019"].task.sscc);
  await fact(p).getByLabel("Собрано всего по строке").fill("2"); await fact(p).getByRole("button", { name: "Внести факт" }).click(); await fact(p).getByText("Факт строки принят").waitFor();
  const marked = JSON.parse(res.posts[0]); assert(marked.unit_scans.length === 2 && marked.unit_scans.every(x => x.system_code === "CRPT" && x.profile_code === "WATER") && marked.scan_product === null && marked.expected_case_signature === L.signature, res.posts[0]);
  ok(w, "FIXTURE marked line: HID codes (duplicate ignored) go as existing unit_scans with the line's marking profile");
  fx.device = "WEIGHT_LABEL_SCAN_REQUIRED"; await scan(p, CUR); await fact(p).getByText("весовая этикетка").waitFor();
  assert(await fact(p).getByRole("button", { name: "Внести факт" }).isDisabled()); fx.device = false; ok(w, "weight-label line: paper entry blocked (TSD only)");
  await scan(p, PAPER["1020"].lines[0].reference); await fact(p).getByText("задание не начато").waitFor(); ok(w, "task not started: paper entry blocked, start stays the normal action");

  fx.queue403 = true; await desk(p).getByRole("button", { name: "Показать задания CASE" }).click();
  await desk(p).getByText("Задания CASE не прочитаны").waitFor(); assert(await desk(p).locator("li").count() === 0); ok(w, "403 clears the CASE queue");
  await ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try { await width(b, 1440, 900); await width(b, 390, 844); assert.deepStrictEqual(res.errors, []); assert.deepStrictEqual(res.liveWrites, []); res.status = "PASS"; }
  catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0156-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length, "checks", JSON.stringify(res.timings));
  process.exit(res.status === "PASS" ? 0 : 1);
})();
