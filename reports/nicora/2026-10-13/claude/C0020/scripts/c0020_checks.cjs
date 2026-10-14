// C-0020: адресные проверки без записи. Все POST перехватываются; ответы и случаи подставляются только здесь.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const [OUT] = process.argv.slice(2);
const ctx = JSON.parse(fs.readFileSync("C:/projects/TMS/tmp/context1348.json", "utf8"));
const J = (route, body, status = 200) => route.fulfill({ status, headers: { "content-type": "application/json", "access-control-allow-origin": "*" }, body: JSON.stringify(body) });
(async () => {
  let input = ""; for await (const part of process.stdin) input += part; const creds = JSON.parse(input);
  const b = await chromium.launch(); const res = {};
  // React: карточка случая после подтверждённого заявления (ответ в форме native: total_tare_changed=null) и отказ хранилища.
  { const p = await b.newPage({ viewport: { width: 430, height: 940 } }); let posts = 0;
    await p.route("**/api/inventory/tare/loss-report", async (route) => { posts++; const body = route.request().postDataJSON(); J(route, { operation_id: body.operation_id, status: "REPORTED", quantity: body.quantity, total_tare_changed: null, goods_stock_changed: false }); });
    await p.goto("http://127.0.0.1:3000/?page=driver&driver_id=10018");
    await p.getByLabel("Пользователь", { exact: true }).fill(creds.driver.username); await p.getByLabel("Пароль", { exact: true }).fill(creds.driver.password);
    await p.getByRole("button", { name: "Войти", exact: true }).click();
    await p.locator("input[type=date]").fill("2026-11-03"); await p.getByText("Рейс #33571", { exact: true }).click(); await p.getByRole("button", { name: "📦 Адреса", exact: true }).click();
    const panel = p.locator(".tare-workspace");
    await panel.getByLabel("Учётная запись", { exact: true }).fill(creds.store.username); await panel.getByLabel("Пароль", { exact: true }).fill(creds.store.password);
    await panel.getByRole("button", { name: "Показать передачи этого рейса", exact: true }).click(); await panel.locator(".tare-history").waitFor();
    await panel.getByLabel("Склад-владелец", { exact: true }).selectOption(String(ctx.warehouse)); await panel.getByLabel("Тип тары", { exact: true }).selectOption(String(ctx.type));
    const form = panel.locator("fieldset").filter({ hasText: "Недостача тары у автомобиля или магазина" });
    async function fill(ref) {
      await form.getByRole("button", { name: "Показать текущую ответственность", exact: true }).click(); await p.waitForTimeout(1000);
      await form.getByLabel("Место и состояние тары", { exact: true }).selectOption("0");
      const c = form.getByLabel("Исходная выдача или акт повреждения", { exact: true }); await c.selectOption((await c.locator("option").nth(1).getAttribute("value")));
      await form.getByLabel("Не обнаружено единиц", { exact: true }).fill("1"); await form.getByLabel("Обстоятельства", { exact: true }).fill("mock only"); await form.getByLabel("Номер акта", { exact: true }).fill(ref);
    }
    await fill("MOCK.C0020.CARD"); await form.getByRole("button", { name: "Заявить недостачу", exact: true }).click();
    const card = panel.locator("section.tare-case[aria-label='Заявление о недостаче']"); await card.waitFor({ timeout: 15000 });
    res.reactCard = { text: (await card.innerText()).replace(/\s+/g, " "), posts }; await card.screenshot({ path: `${OUT}/l6_react_case_card.png` });
    await p.evaluate(() => { Storage.prototype.setItem = function () { throw new DOMException("quota", "QuotaExceededError"); }; });
    const before = posts; await fill("MOCK.C0020.STORAGE"); await form.getByRole("button", { name: "Заявить недостачу", exact: true }).click(); await p.waitForTimeout(800);
    res.reactStorageFailure = { message: await panel.locator("p[role=status].tare-status").textContent(), posts: posts - before };
    await p.close(); }
  // Raw-реестр: автор не решает собственное заявление; отказ хранилища; повреждённая запись.
  { const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); let posts = 0;
    p.on("request", (r) => { if (r.method() === "POST" && r.url().includes("/api/inventory/tare/")) posts++; });
    await p.route("**/api/inventory/tare/loss-decide", (route) => route.abort("failed"));
    await p.route("**/api/inventory/tare/warehouses/9807/loss-cases", (route) => J(route, [{ operation_id: "TARE:mock-own", pallet_type_id: 1, pallet_type_name: "Европоддон", condition_code: "GOOD", quantity: "1", reason_text: "mock", decision_reference: "MOCK-OWN", actor: "admin", created_at: "2026-10-14T12:00:00Z", custodian_kind: "STORE", custodian_id: ctx.store, source_claim_id: "TARE:mock-loan", transport_task_id: null, decision_operation_id: null, outcome: null, decided_by: null }]));
    await p.goto("http://127.0.0.1:5190/tare-loss.html?warehouse_id=9807&claim_id=TARE:mock-own");
    await p.click("#loginFillAdmin"); await p.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit());
    await p.waitForFunction(() => !!document.querySelector('[data-claim="TARE:mock-own"]'), null, { timeout: 30000 });
    res.rawAuthor = { cardButtonDisabled: await p.locator('[data-claim="TARE:mock-own"] button').isDisabled(), why: await p.locator('[data-claim="TARE:mock-own"] .tl-why').textContent(), decideDisabled: await p.isDisabled("#tlDecide"), hint: await p.textContent("#tlDecisionHint") };
    await p.locator('[data-claim="TARE:mock-own"]').screenshot({ path: `${OUT}/l7_author_blocked.png` });
    await p.evaluate(() => { Storage.prototype.setItem = function () { throw new DOMException("quota", "QuotaExceededError"); }; });
    const bal = await p.locator("#tlBalance option").count();
    if (bal) { await p.selectOption("#tlBalance", "0"); await p.fill("#tlQty", "1"); await p.fill("#tlReason", "mock"); await p.fill("#tlReference", "MOCK.STORAGE"); await p.click("#tlReport"); await p.waitForTimeout(500); }
    res.rawStorageFailure = { message: await p.textContent("#tlMessage"), posts };
    await p.close(); }
  { const p = await b.newPage({ viewport: { width: 390, height: 844 } });
    await p.goto("http://127.0.0.1:5190/tare-loss.html"); await p.click("#loginFillAdmin"); await p.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit());
    await p.waitForFunction(() => !document.body.classList.contains("auth-pending"));
    await p.evaluate(() => localStorage.setItem("tare-loss:" + wmsAdminAuth.state.apiBase.replace(/\/$/, "") + ":" + wmsAdminAuth.state.user.username, "{broken"));
    await p.reload(); await p.click("#loginFillAdmin").catch(() => {}); await p.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit()).catch(() => {});
    await p.waitForFunction(() => !document.body.classList.contains("auth-pending")); await p.waitForTimeout(400);
    res.rawDamaged = { message: await p.textContent("#tlMessage"), reportDisabled: await p.isDisabled("#tlReport"), restart: await p.textContent("#tlRestart"), retryHidden: await p.isHidden("#tlRetry"), overflow: await p.evaluate(() => document.documentElement.scrollWidth - innerWidth) };
    await p.evaluate(() => localStorage.clear()); await p.close(); }
  fs.writeFileSync(`${OUT}/../c0020_checks.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
