// C-0008 этап 2: рабочий экран дополнительных расходов.
// Чтение — реальный API стенда. Ответы POST и отдельные реестры с промежуточными стадиями подставляются ТОЛЬКО
// в этом тесте (page.route), реальная запись не выполняется: для полного цикла нужны два сотрудника (см. отчёт).
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const fs = require("fs");
const OUT = process.argv[2];
const PAGE = "http://127.0.0.1:5190/logistics-expenses.html";
const REAL_WARE = 2378876, MOCK_WARE = 990001;
const J = (route, body, status = 200) => route.fulfill({ status, headers: { "content-type": "application/json", "access-control-allow-origin": "*" }, body: JSON.stringify(body) });
const row = (o) => ({ operation_id: "T:" + o.id, article_code: "EX.QA", article_name: o.name || "Платная парковка", object_kind: o.kind || "TRIP", object_id: o.obj || 33514, amount: o.amount || "15.50", currency: o.cur || "GEL",
  expense_date: "2026-10-13", document_reference: "Чек " + o.id, reporter: "logist.a", correction_of_op: null, cost_correction_of_op: null, expected_confirmed_total: null, confirmed_total: o.amount || "15.50",
  logist_operation_id: o.l ? "L:" + o.id : null, logist_outcome: o.l || null, distribution_basis: o.basis || null, logist_actor: o.l ? (o.la || "logist.b") : null,
  finance_operation_id: o.f ? "F:" + o.id : null, finance_outcome: o.f || null, allocation_operation_id: o.a ? "A:" + o.id : null });
const MOCK_ROWS = [row({ id: 1 }), row({ id: 2, l: "APPROVE", basis: "WEIGHT" }), row({ id: 3, l: "APPROVE", basis: "WEIGHT", la: "admin", amount: "7.25" }),
  row({ id: 4, l: "APPROVE", basis: "WEIGHT", f: "APPROVE", cur: "RUB", amount: "100.10" }), row({ id: 5, kind: "VEHICLE", obj: 77, l: "APPROVE", basis: "NONE", f: "APPROVE", amount: "3.00" }),
  row({ id: 6, l: "REJECT", basis: "NONE", amount: "9.99" })];

async function open(b, viewport) {
  const ctx = await b.newContext({ viewport }); const p = await ctx.newPage(); const log = { posts: [], errors: [] };
  p.on("console", (m) => { if (m.type() === "error") log.errors.push(m.text()); });
  p.on("request", (r) => { if (r.method() === "POST" && r.url().includes("/api/finance/")) log.posts.push({ url: r.url().replace(/^.*\/api/, "/api"), body: r.postData() }); });
  await p.goto(PAGE); await p.click("#loginFillAdmin");
  await p.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit());
  await p.waitForFunction(() => !document.body.classList.contains("auth-pending"));
  return { ctx, p, log };
}
async function loadWare(p, ware) { await p.fill("#exWare", String(ware)); await p.click("#exLoad"); await p.waitForFunction(() => /обновлены|не прочитан|Нет прав|не ответил/.test(document.getElementById("exMessage").textContent), null, { timeout: 30000 }); }
const state = (p) => p.evaluate(() => ({ msg: document.getElementById("exMessage").textContent, window: document.getElementById("lxWindow").hidden ? "(скрыто)" : document.getElementById("lxWindow").textContent, shown: document.getElementById("lxShown").textContent,
  stages: [...document.querySelectorAll("#lxStage button")].map((b) => b.textContent), totals: document.getElementById("lxTotals").innerText,
  cards: [...document.querySelectorAll(".lx-card")].map((c) => c.innerText.replace(/\s+/g, " ").slice(0, 260)), pending: document.getElementById("lxPending").hidden ? "" : document.getElementById("lxPending").textContent }));
async function mockRegistry(p, ware, rows, delay = 0) {
  await p.route(new RegExp("logistics-expenses/warehouses/" + ware + "(\\?|$)"), async (r) => { if (delay) await new Promise((x) => setTimeout(x, delay)); return J(r, rows); });
  await p.route(new RegExp("logistics-expenses/warehouses/" + ware + "/normative-costs"), (r) => J(r, []));
}

(async () => {
  const b = await chromium.launch(); const res = {};
  // 1. Реальный реестр склада: desktop и mobile.
  for (const [label, vp] of [["desktop", { width: 1440, height: 1000 }], ["mobile", { width: 390, height: 844 }]]) {
    const { ctx, p, log } = await open(b, vp); await loadWare(p, REAL_WARE); res["real_" + label] = await state(p);
    await p.screenshot({ path: `${OUT}/s2_real_${label}.png`, fullPage: label === "desktop" });
    if (label === "mobile") { await p.locator(".lx-card").first().screenshot({ path: `${OUT}/s2_real_mobile_card.png` }); res.mobileOverflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); }
    // фильтры по загруженному окну
    if (label === "desktop") {
      await p.getByRole("button", { name: /Отклон/ }).click(); res.filterRejected = (await state(p)).shown;
      await p.getByRole("button", { name: /^Все/ }).click(); await p.selectOption("#lxKind", "VEHICLE"); res.filterVehicle = (await state(p)).cards.map((c) => c.slice(0, 90));
      await p.selectOption("#lxKind", "all"); await p.fill("#lxQuery", "DEV.CREDIT"); res.filterQuery = (await state(p)).shown; await p.fill("#lxQuery", "");
      await p.locator(".lx-card", { hasText: "EX.PRECISION" }).getByRole("button", { name: "Скорректировать" }).click().catch(() => {});
      await p.waitForTimeout(500); res.correctPick = await p.evaluate(() => ({ correction: document.getElementById("exCorrection").value, confirmed: document.getElementById("exConfirmed").value, focus: document.activeElement.id }));
      await p.fill("#exAmount", "-5.25"); res.correctionPreview = await p.textContent("#lxReportPreview");
      await p.locator("#lxReportForm").screenshot({ path: `${OUT}/s2_correction_form.png` });
    }
    res["posts_real_" + label] = log.posts.length; res["errors_real_" + label] = log.errors; await ctx.close();
  }
  // 2. Промежуточные стадии (подставленный реестр): следующее действие только выбирает документ.
  { const { ctx, p, log } = await open(b, { width: 1440, height: 1000 }); await mockRegistry(p, MOCK_WARE, MOCK_ROWS); await loadWare(p, MOCK_WARE);
    res.mock = await state(p); await p.screenshot({ path: `${OUT}/s2_stages_desktop.png`, fullPage: true });
    await p.locator("[data-lx-card='T:1']").getByRole("button", { name: "Решение логиста" }).click(); await p.waitForTimeout(500);
    res.nextLogist = await p.evaluate(() => ({ expense: exExpense.value, phase: exPhase.value, basis: exBasis.value, focus: document.activeElement.id, hint: lxDecisionHint.textContent }));
    await p.locator("[data-lx-card='T:2']").getByRole("button", { name: "Решение финконтроля" }).click(); await p.waitForTimeout(500);
    res.nextFinance = await p.evaluate(() => ({ expense: exExpense.value, phase: exPhase.value, basis: exBasis.value, hint: lxDecisionHint.textContent }));
    res.sameActor = await p.locator("[data-lx-card='T:3'] button[data-lx-action]").evaluate((b) => ({ disabled: b.disabled, title: b.title }));
    await p.locator("[data-lx-card='T:4']").getByRole("button", { name: "Распределить на товар" }).click(); await p.waitForTimeout(500);
    res.nextAllocate = await p.evaluate(() => ({ allocation: exAllocation.value, focus: document.activeElement.id }));
    await p.locator("#lxDecideForm").screenshot({ path: `${OUT}/s2_decision_form_prefilled.png` });
    res.postsAfterNextActions = log.posts.length;
    // права: без calc_tt_price/create_tt_price кнопки недоступны с причиной
    await p.evaluate(() => { wmsAdminAuth.state.user.permissions = ["wms_admin_login", "transport_dispatch_view"]; LxPage.render(); });
    res.noRights = await p.locator("button[data-lx-action]").evaluateAll((bs) => bs.map((b) => ({ label: b.textContent, disabled: b.disabled, title: b.title })));
    await ctx.close(); }
  // 3. Устаревший ответ: склад сменили, пока реестр читался.
  { const { ctx, p } = await open(b, { width: 1440, height: 900 }); await mockRegistry(p, MOCK_WARE, MOCK_ROWS, 2500);
    await p.fill("#exWare", String(MOCK_WARE)); await p.click("#exLoad"); await p.waitForTimeout(300); await p.fill("#exWare", String(REAL_WARE)); await p.waitForTimeout(3200);
    res.staleAfterWareChange = await state(p); await ctx.close(); }
  // 4. Неизвестный ответ регистрации → повтор того же operation_id/body; несовпадающий ответ не считается успехом.
  { const { ctx, p, log } = await open(b, { width: 1440, height: 1000 }); await mockRegistry(p, MOCK_WARE, MOCK_ROWS);
    let mode = "abort"; await p.route(/logistics-expenses\/report$/, async (r) => {
      const body = JSON.parse(r.request().postData() || "{}");
      if (mode === "abort") return r.abort("connectionreset");
      if (mode === "mismatch") return J(r, { operation_id: "EXPENSE:other", status: "REPORTED", amount: body.amount, currency: body.currency });
      return J(r, { operation_id: body.operation_id, status: "REPORTED", object_kind: body.object_kind, object_id: body.object_id, amount: body.amount, currency: body.currency, warehouse_id: body.warehouse_id, stock_changed: false }); });
    await loadWare(p, MOCK_WARE); await p.selectOption("#exKind", "TRIP"); await p.fill("#exObject", "33514"); await p.fill("#exAmount", "12.40");
    await p.fill("#exDay", "2026-10-14"); await p.fill("#exReference", "Чек 777"); await p.fill("#exReason", "Тест отображения"); res.newPreview = await p.textContent("#lxReportPreview");
    await p.click("#exReport"); await p.waitForTimeout(600); res.unknown = await state(p);
    res.storedAfterUnknown = await p.evaluate(() => Object.keys(localStorage).filter((k) => k.startsWith("logistics-expenses:")).length);
    res.retryVisible = await p.isVisible("#exRetry"); res.reportDisabledWhilePending = await p.isDisabled("#exReport");
    await p.screenshot({ path: `${OUT}/s2_unknown_result.png` });
    mode = "mismatch"; await p.click("#exRetry"); await p.waitForTimeout(600); res.mismatch = (await state(p)).msg;
    mode = "ok"; await p.click("#exRetry"); await p.waitForTimeout(1200); res.afterRetry = await state(p);
    const bodies = log.posts.filter((x) => x.url.endsWith("/report")).map((x) => x.body); res.sameBodyOnRetry = bodies.length >= 2 && bodies.every((x) => x === bodies[0]); res.reportPosts = bodies.length;
    await ctx.close(); }
  // 5. Повреждённое сохранение блокирует новые команды.
  { const { ctx, p } = await open(b, { width: 1440, height: 900 });
    await p.evaluate(() => { localStorage.setItem("logistics-expenses:" + wmsAdminAuth.state.apiBase.replace(/\/$/, "") + ":" + wmsAdminAuth.state.user.username, "{broken"); });
    await p.reload(); await p.click("#loginFillAdmin").catch(() => {}); await p.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit()).catch(() => {});
    await p.waitForFunction(() => !document.body.classList.contains("auth-pending")); await p.waitForTimeout(300);
    res.damaged = { pending: await p.textContent("#lxPending"), reportDisabled: await p.isDisabled("#exReport"), restart: await p.textContent("#exRestart"), retryHidden: await p.isHidden("#exRetry") };
    await ctx.close(); }
  fs.writeFileSync(`${OUT}/../stage2_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
