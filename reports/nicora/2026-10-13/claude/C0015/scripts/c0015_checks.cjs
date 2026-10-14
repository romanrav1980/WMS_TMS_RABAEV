// C-0015: адресные проверки без записи. Контекст/акты для автора акта подставляются только здесь;
// POST перехватываются и считаются — в Oracle ничего не пишется.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const [OUT] = process.argv.slice(2);
const ctx = JSON.parse(fs.readFileSync("C:/projects/TMS/tmp/context1348.json", "utf8"));
(async () => {
  let input = ""; for await (const part of process.stdin) input += part; const creds = JSON.parse(input);
  const browser = await chromium.launch(); const res = {};
  const page = await browser.newPage({ viewport: { width: 430, height: 940 } }); let posts = 0;
  page.on("request", (r) => { if (r.method() === "POST" && r.url().includes("/api/inventory/tare/")) posts++; });
  await page.route("**/api/inventory/tare/**", (route) => route.request().method() === "POST" ? route.abort("failed") : route.continue());
  // Автор акта с правом списания (подставленный контекст) видит блокировку независимого решения.
  await page.route("**/api/inventory/tare/trips/33571/context", async (route) => { const r = await route.fetch(); const j = await r.json(); j.permissions = { ...(j.permissions || {}), can_writeoff: 1 }; route.fulfill({ response: r, json: j }); });
  await page.goto("http://127.0.0.1:3000/?page=driver&driver_id=10018");
  await page.getByLabel("Пользователь", { exact: true }).fill(creds.driver.username); await page.getByLabel("Пароль", { exact: true }).fill(creds.driver.password);
  await page.getByRole("button", { name: "Войти", exact: true }).click();
  await page.locator("input[type=date]").fill("2026-11-03"); await page.getByText("Рейс #33571", { exact: true }).click(); await page.getByRole("button", { name: "📦 Адреса", exact: true }).click();
  const panel = page.locator(".tare-workspace");
  await panel.getByLabel("Учётная запись", { exact: true }).fill(creds.store.username); await panel.getByLabel("Пароль", { exact: true }).fill(creds.store.password);
  await panel.getByRole("button", { name: "Показать передачи этого рейса", exact: true }).click(); await panel.locator(".tare-history").waitFor();
  await panel.getByLabel("Склад-владелец", { exact: true }).selectOption(String(ctx.warehouse)); await panel.getByLabel("Тип тары", { exact: true }).selectOption(String(ctx.type));
  await page.route("**/api/inventory/tare/warehouses/9807/damage-cases", (route) => route.fulfill({ json: [{ operation_id: "TARE:mock-open", owner_ware_id: 9807, pallet_type_id: 1, pallet_type_name: "Европоддон", custodian_kind: "STORE", custodian_id: ctx.store, delivery_accept_operation_id: "TARE:mock-loan", damaged_quantity: "2", written_off_quantity: "0", reason_text: "mock", decision_reference: "MOCK-AUTHOR", actor: creds.store.username, created_at: "2026-10-14T12:00:00Z" }] }));
  await page.route("**/api/inventory/tare/warehouses/9807/damage-custody", (route) => route.fulfill({ json: { warehouse_id: 9807, items: [{ damage_operation_id: "TARE:mock-open", pallet_type_id: 1, custodian_kind: "STORE", custodian_id: ctx.store, tracked_quantity: "2" }], has_more: false } }));
  await panel.getByRole("button", { name: "Показать акты повреждения", exact: true }).click(); await page.waitForTimeout(600);
  const form = panel.locator("fieldset.tare-writeoff");
  await form.getByLabel("Акт повреждения для списания", { exact: true }).selectOption("TARE:mock-open");
  await form.getByLabel("Списать единиц", { exact: true }).fill("3");
  res.authorBlocked = { message: await form.locator("p[role=status]").textContent(), tooMany: await form.locator("p[role=alert]").count(), buttonDisabled: await form.getByRole("button", { name: "Списать повреждённую тару", exact: true }).isDisabled() };
  await form.screenshot({ path: `${OUT}/t7_author_blocked.png` });
  // Отказ хранилища: акт повреждения не отправляется.
  await page.evaluate(() => { Storage.prototype.setItem = function () { throw new DOMException("quota", "QuotaExceededError"); }; });
  const damage = panel.locator("fieldset").filter({ hasText: "Осмотр повреждённой тары" });
  await damage.getByRole("button", { name: "Показать исходные выдачи", exact: true }).click(); await page.waitForTimeout(800);
  const loan = await damage.getByLabel("Выдача магазину", { exact: true }).locator("option").nth(1).getAttribute("value");
  await damage.getByLabel("Выдача магазину", { exact: true }).selectOption(loan);
  await damage.getByLabel("Повреждено единиц", { exact: true }).fill("1"); await damage.getByLabel("Результат осмотра", { exact: true }).fill("must not be sent"); await damage.getByLabel("Номер акта", { exact: true }).fill("DEV.C0015.STORAGE-FAIL");
  await damage.getByRole("button", { name: "Зафиксировать повреждение", exact: true }).click(); await page.waitForTimeout(600);
  res.storageFailure = { message: await panel.locator("p[role=status].tare-status").textContent(), posts, retryShown: await panel.getByRole("button", { name: "Повторить сохранённую операцию", exact: true }).count() };
  fs.writeFileSync(`${OUT}/../c0015_checks.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
