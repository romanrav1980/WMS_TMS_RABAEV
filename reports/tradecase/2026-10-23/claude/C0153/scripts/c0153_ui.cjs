// C-0153 UI рабочего места «Исключения» (проведение списания) на frontend (dev :3021) при 1440 и 390.
// ЖИВОЕ (только GET): вход admin, список складов. FIXTURE: весь /exceptions/** (миграция дел качества не применена).
// Любой не-GET вне /exceptions/ прерывается и записывается как нарушение.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0153_BASE || "http://127.0.0.1:3021/", WH = 220793322;
const res = { base: BASE, checks: [], liveWrites: [], errors: [], posts: [], paths: [], timings: {} };
const cors = { "access-control-allow-origin": "*" };
const comp = [{ sku_id: "SKU-1", owner_id: "SNS", base_uom: "EA", base_qty: "40", units: 4 }];
const kase = (id, state, extra) => ({ case_id: id, warehouse_id: WH, pallet_uid: "P" + id, cell: "Q-0" + id, state, version: 2, quality_hold_id: 50 + id,
  reason: "вздутие упаковки", decision_note: state === "OPEN" ? null : "заключение", approval_note: state === "WAITING_POSTING" ? "акт 17" : null,
  opened_by: "qc", opened_at: "2026-10-23T07:00:00Z", decided_by: state === "OPEN" ? null : "qc", decided_at: state === "OPEN" ? null : "2026-10-23T07:30:00Z",
  approved_by: state === "WAITING_POSTING" ? "boss" : null, approved_at: null, posting_status: state === "WAITING_POSTING" ? "WAITING_NATIVE_POSTING" : null, composition: comp, ...extra });
const SNAP = () => ({ warehouse_id: WH, observed_at: new Date().toISOString().replace(/\.\d+Z$/, "Z"),
  quarantine: [{ pallet_uid: "P1", cell: "Q-01", article: "SKU-1", base_qty: "40", base_uom: "EA", stock_version: 3, case_id: 1 },
    { pallet_uid: "P9", cell: "Q-09", article: "SKU-9", base_qty: "12", base_uom: "EA", stock_version: 1, case_id: null }],
  cases: [kase(1, "OPEN"), kase(2, "DEFECT"), kase(3, "WAITING_POSTING"),
    kase(4, "POSTED", { posted_by: "boss", posted_at: "2026-10-23T08:00:00Z", post_operation_id: "exc-x", external_status: "PENDING", posting_status: "POSTED", approved_at: "2026-10-23T07:50:00Z" })],
  discrepancies: fx.closed ? null : [{ inventory_task_id: 77, status: "DONE", cell: "A-01", article: "SKU-5", planned_qty: "10", fact_qty: "8", revision_id: 4, assigned_to: "keeper", updated_at: null }] });
let fx = {};

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (u.includes("/exceptions")) {
    if (m === "GET") {
      if (u.includes("/cases/")) return r.fulfill({ json: { ...kase(1, "OPEN"), units: [{ unit_key: "U-1", sku_id: "SKU-1", base_uom: "EA", base_qty: "10", owner_id: "SNS", unchanged: true }], events: [] }, headers: cors });
      if (fx.late) { const late = fx.late; fx.late = null; await new Promise(x => setTimeout(x, late));
        return r.fulfill({ json: { ...SNAP(), quarantine: [{ pallet_uid: "P-LATE", cell: "Q-99", article: "X", base_qty: "1", base_uom: "EA", stock_version: 1, case_id: null }] }, headers: cors }); }
      if (fx.unavailable) return r.fulfill({ status: 503, json: { detail: { code: "QUALITY_NOT_AVAILABLE", outcome_confirmed: false, retry_same_operation_id: true } }, headers: cors });
      if (fx.read403) return r.fulfill({ status: 403, json: { detail: { code: "QUALITY_ACCESS_DENIED" } }, headers: cors });
      return r.fulfill({ json: SNAP(), headers: cors });
    }
    const body = req.postData(); res.posts.push(body); res.paths.push(u);
    const reply = fx.replies.shift();
    if (reply === 503) return r.fulfill({ status: 503, json: { detail: { code: "QUALITY_RESULT_UNKNOWN", outcome_confirmed: false, retry_same_operation_id: true } }, headers: cors });
    if (typeof reply === "string" && reply !== "foreign") return r.fulfill({ status: 409, json: { detail: { code: reply, outcome_confirmed: true, retry_same_operation_id: false } }, headers: cors });
    const op = reply === "foreign" ? "exc-someone-else" : JSON.parse(body).operation_id;
    return r.fulfill({ json: { ...kase(1, "OPEN"), operation_id: op, replayed: false }, headers: cors });
  }
  if (m !== "GET") { res.liveWrites.push(m + " " + u); return r.abort(); }
  return r.continue();
}

const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };
const desk = p => p.locator("[aria-label='Исключения склада']");
const tab = (p, name) => desk(p).getByRole("tab", { name: new RegExp("^" + name) });

async function enter(p) {
  const login = p.locator("input[type=password]");
  await Promise.race([login.waitFor({ timeout: 30000 }), desk(p).waitFor({ timeout: 30000 })]);
  if (await login.count()) { await p.fill("input[autocomplete=username]", "admin"); await login.fill(pass); await p.click("button[type=submit]"); }
  await desk(p).getByText("Снимок сервера").waitFor({ timeout: 30000 });
}

async function width(b, w, h) {
  fx = { replies: [] };
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await p.route(u => u.href.includes(":8088/api/"), route);
  const t0 = Date.now();
  await p.goto(`${BASE}?page=workspace&workspace=exceptions&warehouse_id=${WH}`); await enter(p);
  (res.timings.desk_ready_ms ??= []).push(Date.now() - t0);
  const d = desk(p), text = await d.innerText();
  for (const s of ["Карантин · 2", "Дела качества · 4", "Расхождения пересчёта · 1", "P1", "дело 1: Ждёт решения контролёра", "дела качества нет"]) assert(text.includes(s), s);
  ok(w, "sections, quarantine pallets and their case state");
  const p1 = d.locator("li", { hasText: "P1" });
  assert(await p1.getByRole("button", { name: "Выпустить" }).getAttribute("aria-disabled") === "true" || await p1.getByRole("button", { name: "Выпустить" }).isDisabled()
    || (await p1.getByRole("button", { name: "Выпустить" }).getAttribute("title")).includes("Недоступно"));
  ok(w, "release is unavailable while a case holds the pallet");
  const bad = await d.locator("button").evaluateAll(bs => bs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every button has title and help id");
  const scroll = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  assert(scroll <= 1, "horizontal scroll " + scroll); ok(w, "no horizontal page scroll");
  await d.screenshot({ path: path.join(SHOTS, `quarantine-${w}.png`) });

  // Открыть дело: 503 → команда сохранена, переживает перезагрузку; повтор — те же байты.
  fx.replies = [503];
  const p9 = d.locator("li", { hasText: "P9" });
  await p9.getByRole("button", { name: "Открыть дело" }).click();
  await p9.getByLabel("Основание (что с товаром)").fill("пятна на коробах"); await p9.locator("button[data-help-id='exceptions.confirm']").click();
  await d.getByText("не подтверждена").waitFor(); ok(w, "503 keeps the command as unconfirmed");
  assert.deepStrictEqual({ ...JSON.parse(res.posts.at(-1)), operation_id: 0 }, { operation_id: 0, action: "OPEN", pallet_uid: "P9", reason: "пятна на коробах" });
  await p.reload(); await enter(p); await desk(p).getByText("не подтверждена").waitFor(); ok(w, "unconfirmed command survives reload");
  fx.replies = ["foreign"]; await desk(p).getByRole("button", { name: "Повторить" }).click();
  await desk(p).getByText("не относится к этой команде").waitFor(); ok(w, "foreign receipt keeps the command");
  fx.replies = [200]; await desk(p).getByRole("button", { name: "Повторить" }).click(); await desk(p).getByText("Выполнено:").waitFor();
  assert.strictEqual(res.posts.at(-1), res.posts.at(-3)); ok(w, "retries resend identical bytes with the same operation_id");

  // Дела: решение контролёра с конфликтом версии, утверждение списания, ожидание проведения, коды.
  await tab(p, "Дела качества").click();
  const c1 = desk(p).locator("li", { hasText: "Дело 1" });
  fx.replies = ["VERSION_CONFLICT"]; await c1.getByRole("button", { name: "Брак" }).click();
  await c1.getByLabel("Заключение контролёра").fill("брак подтверждён"); await c1.locator("button[data-help-id='exceptions.confirm']").click();
  await desk(p).getByText("Дело уже изменено другим пользователем").waitFor();
  assert.deepStrictEqual({ ...JSON.parse(res.posts.at(-1)), operation_id: 0 }, { operation_id: 0, action: "DECIDE", case_id: 1, expected_version: 2, decision: "DEFECT", note: "брак подтверждён" });
  assert.strictEqual(await desk(p).getByText("не подтверждена").count(), 0); ok(w, "decision 409 clears the command with a reason");
  fx.replies = [200]; const c2 = desk(p).locator("li", { hasText: "Дело 2" });
  await c2.getByRole("button", { name: "Утвердить списание" }).click(); await c2.getByLabel("Основание утверждения (документ)").fill("акт 18");
  await c2.locator("button[data-help-id='exceptions.confirm']").click(); await desk(p).getByText("Выполнено:").waitFor();
  assert.strictEqual(JSON.parse(res.posts.at(-1)).action, "APPROVE"); ok(w, "management approves the write-off of a defect");
  const c3 = desk(p).locator("li", { hasText: "Дело 3" });
  assert((await c3.innerText()).includes("ещё не проведено") && await c3.getByRole("button", { name: "Утвердить списание" }).count() === 0);
  ok(w, "approved write-off is shown as waiting for posting, not as posted");
  // Проведение: 503 → команда сохранена; повтор теми же байтами; подтверждённый отказ native-удержания объясняется.
  fx.replies = [503]; await c3.getByRole("button", { name: "Провести списание" }).click();
  await c3.getByRole("button", { name: "Подтвердить проведение" }).click(); await desk(p).getByText("не подтверждена").waitFor();
  assert.deepStrictEqual({ ...JSON.parse(res.posts.at(-1)), operation_id: 0 }, { operation_id: 0, case_id: 3, expected_version: 2 });
  assert(res.paths.at(-1).endsWith("/exceptions/write-offs")); ok(w, "write-off posts the case and version to the native posting command");
  fx.replies = [200]; await desk(p).getByRole("button", { name: "Повторить" }).click(); await desk(p).getByText("Выполнено: проведение списания").waitFor();
  assert.strictEqual(res.posts.at(-1), res.posts.at(-2)); ok(w, "write-off retry resends identical bytes");
  fx.replies = ["QUALITY_WRITE_OFF_EXACT_FROZEN_UNITS_REQUIRED"]; await c3.getByRole("button", { name: "Провести списание" }).click();
  await c3.getByRole("button", { name: "Подтвердить проведение" }).click(); await desk(p).getByText("Коды паллеты не совпадают").waitFor();
  ok(w, "native refusal of a changed composition is explained");
  const c4 = desk(p).locator("li", { hasText: "Дело 4" });
  const t4 = await c4.innerText();
  assert(t4.includes("Списано со склада") && t4.includes("ответ SAP/СКМ ожидается") && await c4.getByRole("button", { name: "Провести списание" }).count() === 0);
  ok(w, "posted case shows the stock write-off and the pending external answer separately");
  await c1.getByRole("button", { name: "Коды" }).click(); await c1.getByText("U-1 · SKU-1").waitFor(); ok(w, "case codes with owner and quantity");
  await desk(p).screenshot({ path: path.join(SHOTS, `cases-${w}.png`) });

  // Расхождения: список и закрытый раздел.
  await tab(p, "Расхождения").click(); await desk(p).getByText("Пересчёт 77").waitFor(); ok(w, "count discrepancy listed");
  fx.closed = true; await desk(p).getByRole("button", { name: "Обновить" }).click(); await desk(p).getByText("Раздел закрыт").waitFor();
  ok(w, "no inventory right: section closed, not empty"); fx.closed = false;

  // Поздний ответ, недоступность и 403.
  await tab(p, "Карантин").click();
  fx.late = 2500; await desk(p).getByRole("button", { name: "Обновить" }).click(); await p.waitForTimeout(200);
  await desk(p).getByRole("button", { name: "Обновить" }).click({ timeout: 500 }); await p.waitForTimeout(3200);
  assert(fx.late === null && await desk(p).getByText("P-LATE").count() === 0); ok(w, "late response of an older read is ignored");
  fx.unavailable = true; await desk(p).getByRole("button", { name: "Обновить" }).click();
  await desk(p).getByText("Учёт дел качества на сервере ещё не включён").waitFor(); ok(w, "not applied is explicit"); fx.unavailable = false;
  fx.read403 = true; await desk(p).getByRole("button", { name: "Обновить" }).click(); await desk(p).getByText("Нет права просмотра").waitFor();
  assert.strictEqual(await desk(p).getByText("P1").count(), 0); ok(w, "403 clears the data");
  await ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try { await width(b, 1440, 900); await width(b, 390, 844); }
  catch (e) { res.errors.push(String(e.stack || e)); console.error(e); }
  finally { await b.close(); }
  assert.deepStrictEqual(res.liveWrites, []);
  fs.writeFileSync(path.join(OUT, "c0153-ui.json"), JSON.stringify({ ...res, posts: res.posts.length }, null, 1));
  console.log(res.errors.length ? "FAIL" : "OK", res.checks.length, "checks");
  process.exit(res.errors.length ? 1 : 0);
})();
