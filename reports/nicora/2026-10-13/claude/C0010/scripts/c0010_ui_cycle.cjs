// C-0010: реальный цикл допрасхода через UI на собственном dev-рейсе 33571 / складе 9807.
// Учётные данные приходят только из окружения (c0010_fixture_cycle.py) и нигде не выводятся.
// Сценарий идемпотентен: шаг выполняется по фактической стадии карточки, повторный запуск не создаёт дублей.
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const fs = require("fs");
const OUT = process.argv[2];
const PAGE = "http://127.0.0.1:5190/logistics-expenses.html";
const A = { user: process.env.C0010_A_USER, pw: process.env.C0010_A_PW }, B = { user: process.env.C0010_B_USER, pw: process.env.C0010_B_PW };
const WARE = "9807", TRIP = "33571", DAY = "2026-10-14", ARTICLE = "DEV.C0010.PARKING";
const DOC = "DEV.C0010.DOC-1", CORR = "DEV.C0010.CORR-1";
const log = [];
const step = (name, data) => { log.push({ name, ...data }); console.log(JSON.stringify({ name, ...data })); };

async function session(b, who, viewport = { width: 1440, height: 1000 }) {
  const ctx = await b.newContext({ viewport }); const p = await ctx.newPage(); const posts = [];
  p.on("request", (r) => { if (r.method() === "POST" && r.url().includes("/api/finance/")) posts.push({ url: r.url().replace(/^.*\/api/, "/api"), body: r.postData() }); });
  await p.goto(PAGE); await p.fill("#loginUser", who.user); await p.fill("#loginPassword", who.pw);
  await p.locator("#loginPassword").evaluate((el) => el.closest("form").requestSubmit());
  await p.waitForFunction(() => !document.body.classList.contains("auth-pending"), null, { timeout: 20000 });
  await p.fill("#exWare", WARE); await p.click("#exLoad"); await msg(p, /обновлены/);
  return { ctx, p, posts };
}
async function msg(p, rx) {
  await p.waitForFunction((src) => { const m = document.getElementById("exMessage"); return new RegExp(src).test(m.textContent) || m.dataset.tone === "error"; }, rx.source, { timeout: 40000 });
  const t = await p.textContent("#exMessage"); if (!rx.test(t)) throw Error("UI: " + t); return t;
}
const card = (p, doc) => p.locator(".lx-card", { hasText: doc });
async function stage(p, doc) { const c = card(p, doc); return (await c.count()) ? (await c.first().getAttribute("class")).match(/lx-card-(\w+)/)[1] : null; }
const opOf = async (p, doc) => (await card(p, doc).first().getAttribute("data-lx-card"));

async function decide(p, doc, label, ref, basis) {
  await card(p, doc).first().getByRole("button", { name: label }).click(); await p.waitForTimeout(400);
  const prefilled = await p.evaluate(() => ({ expense: exExpense.value, phase: exPhase.value, basis: exBasis.value, hint: lxDecisionHint.textContent }));
  if (basis) await p.selectOption("#exBasis", basis);
  await p.fill("#exDecisionRef", ref); await p.fill("#exDecisionReason", "Own C0010 dev cycle: " + label);
  await p.click("#exDecide"); return { prefilled, message: await msg(p, /сохранено|подтверждён|отклонён/) };
}
async function allocate(p, doc) {
  await card(p, doc).first().getByRole("button", { name: "Распределить на товар" }).click(); await p.waitForTimeout(400);
  await p.click("#exAllocate"); return await msg(p, /Распределение/);
}
async function register(p, fields) {
  for (const [id, v] of Object.entries(fields)) { if (id === "exKind" || id === "exArticleSelect") await p.selectOption("#" + id, v); else await p.fill("#" + id, v); }
  const preview = await p.textContent("#lxReportPreview"); await p.click("#exReport"); return { preview, message: await msg(p, /зарегистрирован/) };
}

(async () => {
  const b = await chromium.launch();
  // 0. Статья (финконтроль: create_tt_price) через существующую форму.
  { const { ctx, p } = await session(b, B);
    const exists = await p.evaluate((code) => (LxPage.articles() || []).some((a) => a.code === code), ARTICLE);
    if (!exists) { await p.fill("#exCode", ARTICLE); await p.fill("#exName", "DEV C0010 own trip parking expense"); await p.selectOption("#exScope", "TRIP");
      await p.setChecked("#exIncluded", false); await p.setChecked("#exActive", true); await p.click("#exArticle"); step("article", { message: await msg(p, /Статья/) }); }
    else step("article", { message: "уже существует" });
    await ctx.close(); }
  // 1. Регистрация исходного расхода и решение логиста (A).
  let a = await session(b, A);
  if (!(await stage(a.p, DOC))) { await a.p.selectOption("#exKind", "TRIP"); await a.p.waitForTimeout(100);
    step("report", await register(a.p, { exArticleSelect: ARTICLE, exObject: TRIP, exAmount: "12.34", exCurrency: "GEL", exDay: DAY, exReference: DOC, exReason: "Own C0010 dev trip parking" })); }
  if ((await stage(a.p, DOC)) === "await_logist") step("logist", await decide(a.p, DOC, "Решение логиста", "DEV.C0010.LOG-1", "BASE_QUANTITY"));
  step("after_logist_A", { finance_button: await card(a.p, DOC).first().locator("button[data-lx-action]").first().evaluate((x) => ({ text: x.textContent, disabled: x.disabled, title: x.title })).catch(() => null) });
  await a.ctx.close();
  // 2. Финконтроль (B).
  let f = await session(b, B);
  if ((await stage(f.p, DOC)) === "await_finance") step("finance", await decide(f.p, DOC, "Решение финконтроля", "DEV.C0010.FIN-1"));
  await f.ctx.close();
  // 3. Распределение (A) и повтор той же операции.
  a = await session(b, A);
  if ((await stage(a.p, DOC)) === "await_allocation") {
    step("allocate", { message: await allocate(a.p, DOC) });
    const sent = a.posts.find((x) => x.url.endsWith("/expense-allocation"));
    const replay = await a.p.evaluate(async (body) => { const r = await fetch(wmsAdminAuth.state.apiBase.replace(/\/$/, "") + "/api/finance/expense-allocation", { method: "POST", headers: wmsAdminAuth.headers({ "Content-Type": "application/json" }), body }); return { status: r.status, body: await r.json() }; }, sent.body);
    step("allocate_replay_same_operation", { sent: JSON.parse(sent.body), status: replay.status, operation_id: replay.body.operation_id, result_status: replay.body.status, amount: replay.body.amount, lines: (replay.body.lines || []).map((l) => l.amount), stock_changed: replay.body.stock_changed });
  }
  // 4. Корректировка со знаком (A) и решение логиста по ней.
  if (!(await stage(a.p, CORR))) {
    await card(a.p, DOC).first().getByRole("button", { name: "Скорректировать" }).click(); await a.p.waitForTimeout(400);
    step("correction_report", await register(a.p, { exAmount: "-2.10", exDay: DAY, exReference: CORR, exReason: "Own C0010 dev correction: part refunded" })); }
  if ((await stage(a.p, CORR)) === "await_logist") step("correction_logist", await decide(a.p, CORR, "Решение логиста", "DEV.C0010.LOG-2"));
  await a.ctx.close();
  f = await session(b, B);
  if ((await stage(f.p, CORR)) === "await_finance") step("correction_finance", await decide(f.p, CORR, "Решение финконтроля", "DEV.C0010.FIN-2"));
  await f.ctx.close();
  a = await session(b, A);
  if ((await stage(a.p, CORR)) === "await_allocation") step("correction_allocate", { message: await allocate(a.p, CORR) });
  step("final", { original: await stage(a.p, DOC), correction: await stage(a.p, CORR), original_card: (await card(a.p, DOC).first().innerText()).replace(/\s+/g, " "), correction_card: (await card(a.p, CORR).first().innerText()).replace(/\s+/g, " "), totals: await a.p.textContent("#lxTotals") });
  // точный поиск по ID исходного расхода
  await a.p.fill("#lxExactId", await opOf(a.p, DOC)); await a.p.click("#lxExactFind"); step("exact_search", { message: await msg(a.p, /найден/) }); await a.p.fill("#lxQuery", "DEV.C0010"); await a.p.dispatchEvent("#lxQuery", "input");
  await a.p.screenshot({ path: `${OUT}/c1_cycle_desktop.png`, fullPage: false }); await card(a.p, DOC).first().screenshot({ path: `${OUT}/c1_original_card.png` }); await card(a.p, CORR).first().screenshot({ path: `${OUT}/c1_correction_card.png` });
  await a.ctx.close();
  const m = await session(b, A, { width: 390, height: 844 }); await m.p.fill("#lxQuery", "DEV.C0010"); await m.p.dispatchEvent("#lxQuery", "input");
  await card(m.p, DOC).first().scrollIntoViewIfNeeded(); await m.p.screenshot({ path: `${OUT}/c1_cycle_mobile.png` });
  step("mobile", { overflow: await m.p.evaluate(() => document.documentElement.scrollWidth - innerWidth) }); await m.ctx.close();
  // 5. Отказ хранилища: намерение не записывается → POST не отправляется (реальной записи нет).
  const s = await session(b, A);
  await s.p.evaluate(() => { Storage.prototype.setItem = function () { throw new DOMException("quota", "QuotaExceededError"); }; });
  await s.p.selectOption("#exKind", "TRIP"); await s.p.selectOption("#exArticleSelect", ARTICLE);
  for (const [id, v] of Object.entries({ exObject: TRIP, exAmount: "1.00", exCurrency: "GEL", exDay: DAY, exReference: "DEV.C0010.STORAGE-FAIL", exReason: "must not be sent" })) await s.p.fill("#" + id, v);
  await s.p.click("#exReport"); await s.p.waitForTimeout(800);
  step("storage_failure", { message: await s.p.textContent("#exMessage"), posts: s.posts.length, pendingShown: !(await s.p.isHidden("#lxPending")), reportEnabledAfter: await s.p.isEnabled("#exReport") });
  await s.p.screenshot({ path: `${OUT}/c1_storage_failure.png` }); await s.ctx.close();
  fs.writeFileSync(`${OUT}/../c0010_ui_steps.json`, JSON.stringify(log, null, 1)); await b.close();
})().catch((e) => { console.error(String(e && e.stack || e).slice(0, 1500)); fs.writeFileSync(`${OUT}/../c0010_ui_steps.json`, JSON.stringify(log, null, 1)); process.exit(1); });
