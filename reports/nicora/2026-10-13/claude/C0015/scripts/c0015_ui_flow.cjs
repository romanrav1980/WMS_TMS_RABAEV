// C-0015: повреждённая оборотная тара через существующий TarePanel (страница водителя, рейс 33571).
// Учётные данные приходят через stdin и не выводятся. Каждый шаг выполняется по фактической стадии карточки акта,
// поэтому повторный запуск не создаёт второго повреждения/передачи/списания.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const [OUT] = process.argv.slice(2);
const ctx = JSON.parse(fs.readFileSync("C:/projects/TMS/tmp/context1348.json", "utf8"));
const DAMAGE_REF = "DEV.C0015.DAMAGE-1", WRITEOFF_REF = "DEV.C0015.WRITEOFF-1";
const facts = [], errors = [];
const log = (name, data) => { facts.push({ name, ...data }); console.log(JSON.stringify({ name, ...data }).slice(0, 900)); };
const save = () => fs.writeFileSync(`${OUT}/../c0015_ui_facts.json`, JSON.stringify({ facts, errors }, null, 1));

(async () => {
  let input = ""; for await (const part of process.stdin) input += part; const creds = JSON.parse(input);
  const browser = await chromium.launch();
  async function open(role, viewport = { width: 430, height: 940 }) {
    const page = await browser.newPage({ viewport }); page.on("pageerror", (e) => errors.push(role + ": " + e.message));
    await page.goto("http://127.0.0.1:3000/?page=driver&driver_id=10018");
    await page.getByLabel("Пользователь", { exact: true }).fill(creds.driver.username);
    await page.getByLabel("Пароль", { exact: true }).fill(creds.driver.password);
    await page.getByRole("button", { name: "Войти", exact: true }).click();
    await page.locator("input[type=date]").fill("2026-11-03"); await page.getByText("Рейс #33571", { exact: true }).click();
    await page.getByRole("button", { name: "📦 Адреса", exact: true }).click();
    const panel = page.locator(".tare-workspace");
    await panel.getByLabel("Учётная запись", { exact: true }).fill(creds[role].username); await panel.getByLabel("Пароль", { exact: true }).fill(creds[role].password);
    await panel.getByRole("button", { name: "Показать передачи этого рейса", exact: true }).click(); await panel.locator(".tare-history").waitFor();
    await panel.getByLabel("Склад-владелец", { exact: true }).selectOption(String(ctx.warehouse)); await panel.getByLabel("Тип тары", { exact: true }).selectOption(String(ctx.type));
    return { page, panel };
  }
  const status = (panel, text) => panel.locator("p[role=status].tare-status").filter({ hasText: text }).waitFor({ timeout: 30000 });
  async function cases(s) {
    await s.panel.getByRole("button", { name: "Показать передачи этого рейса", exact: true }).click(); await s.page.waitForTimeout(500);
    await s.panel.getByLabel("Склад-владелец", { exact: true }).selectOption(String(ctx.warehouse)); await s.panel.getByLabel("Тип тары", { exact: true }).selectOption(String(ctx.type));
    await s.panel.getByRole("button", { name: "Показать акты повреждения", exact: true }).click(); await s.page.waitForTimeout(1200);
    const card = s.panel.locator(".tare-case", { hasText: "Акт " + DAMAGE_REF });
    return { card, step: (await card.count()) ? await card.locator(".tare-chip").textContent() : null };
  }
  async function post(s, path, button, scope) {
    const response = s.page.waitForResponse((r) => r.url().endsWith("/api/inventory/tare" + path) && r.request().method() === "POST");
    await scope.getByRole("button", { name: button, exact: true }).click(); const r = await response; const body = await r.json();
    log(path, { status: r.status(), request: r.request().postDataJSON(), result: body }); save(); if (!r.ok()) throw Error(path + " " + JSON.stringify(body));
    return body;
  }
  async function acceptOffer(s, qty) {
    await s.panel.getByRole("button", { name: "Показать передачи этого рейса", exact: true }).click();
    const form = s.panel.locator("fieldset").filter({ hasText: "Фактически принято тары" }).filter({ hasText: "DAMAGED" }).first(); await form.waitFor({ timeout: 20000 });
    await form.getByLabel("Фактически принято тары", { exact: true }).fill(String(qty)); await form.getByLabel("Скан машины", { exact: true }).fill(ctx.plate);
    return post(s, "/accept", "Получатель принял тару", form);
  }
  async function offerFromCard(s, label) {
    const { card } = await cases(s); await card.getByRole("button", { name: label, exact: true }).click();
    const form = s.panel.locator("fieldset.tare-offer");
    await s.page.waitForFunction(() => { const sel = document.querySelector('.tare-workspace select[aria-label="Акт повреждения"]'); return sel && sel.value; }, null, { timeout: 20000 });
    const prefilled = await form.evaluate((f) => Object.fromEntries([...f.querySelectorAll("select")].map((x) => [x.getAttribute("aria-label"), x.value])));
    log("prefilled_" + label, { prefilled });
    await form.getByLabel("Количество тары", { exact: true }).fill("1"); await form.getByLabel("Скан машины", { exact: true }).fill(ctx.plate);
    return post(s, "/offer", "Предложить передачу", form);
  }

  const store = await open("store");
  // 1. Повреждение одной GOOD-единицы у магазина со ссылкой на исходную выдачу.
  let st = await cases(store);
  if (!st.step) {
    const form = store.panel.locator("fieldset").filter({ hasText: "Осмотр повреждённой тары" });
    await form.getByRole("button", { name: "Показать исходные выдачи", exact: true }).click(); await store.page.waitForTimeout(800);
    const loan = await form.getByLabel("Выдача магазину", { exact: true }).locator("option").nth(1).getAttribute("value");
    await form.getByLabel("Выдача магазину", { exact: true }).selectOption(loan);
    await form.getByLabel("Повреждено единиц", { exact: true }).fill("1"); await form.getByLabel("Результат осмотра", { exact: true }).fill("Own C0015 dev: broken deck board found at store");
    await form.getByLabel("Номер акта", { exact: true }).fill(DAMAGE_REF);
    await post(store, "/damage", "Зафиксировать повреждение", form); await status(store.panel, "Повреждение зафиксировано");
    st = await cases(store);
  }
  log("after_damage", { step: st.step, card: st.step ? (await st.card.innerText()).replace(/\s+/g, " ") : null });
  await st.card.screenshot({ path: `${OUT}/t1_damage_case_store.png` }).catch(() => {});
  // 2. Возврат магазин → водитель со ссылкой на акт.
  if (st.step === "Вернуть водителю") { await offerFromCard(store, "Вернуть водителю"); await status(store.panel, "Передача предложена"); }
  const driver = await open("driver");
  if ((await driver.panel.locator("fieldset").filter({ hasText: "Фактически принято тары" }).filter({ hasText: "DAMAGED" }).count()) || true) {
    const d = await cases(driver);
    if (d.step === "Вернуть водителю") { await acceptOffer(driver, 1); await status(driver.panel, "Приёмка тары проведена"); }
  }
  // 3. Возврат водитель → склад.
  let d2 = await cases(driver);
  if (d2.step === "Вернуть на склад") { await offerFromCard(driver, "Вернуть на склад"); await status(driver.panel, "Передача предложена"); }
  const admin = await open("admin");
  let a = await cases(admin);
  if (a.step === "Вернуть на склад") { await acceptOffer(admin, 1); await status(admin.panel, "Приёмка тары проведена"); }
  a = await cases(admin); log("before_writeoff", { step: a.step, card: (await a.card.innerText()).replace(/\s+/g, " ") });
  // 4. Автор акта не может списать: проверка UI-подсказки у магазина (права списания у него нет).
  log("store_writeoff_visible", { visible: await store.panel.locator("fieldset.tare-writeoff").count() });
  // 5. Независимое решение о списании; первый ответ теряется браузером — повтор того же ID.
  const approver = await open("approver", { width: 1280, height: 900 });
  let ap = await cases(approver);
  if (ap.step === "Решение о списании") {
    await ap.card.getByRole("button", { name: "Решение о списании", exact: true }).click(); await approver.page.waitForTimeout(400);
    const form = approver.panel.locator("fieldset.tare-writeoff");
    log("writeoff_prefilled", { damage: await form.getByLabel("Акт повреждения для списания", { exact: true }).inputValue(), hint: await form.locator(".tare-next").textContent() });
    await form.getByLabel("Списать единиц", { exact: true }).fill("1"); await form.getByLabel("Основание решения", { exact: true }).fill("Own C0015 dev: deck board not repairable");
    await form.getByLabel("Номер решения", { exact: true }).fill(WRITEOFF_REF);
    await approver.page.route("**/api/inventory/tare/writeoff", async (route) => {
      const response = await route.fetch(); const body = await response.json();
      log("writeoff_lost_response", { status: response.status(), request: route.request().postDataJSON(), result: body }); save(); await route.abort("failed");
    }, { times: 1 });
    await form.getByRole("button", { name: "Списать повреждённую тару", exact: true }).click();
    const retry = approver.panel.getByRole("button", { name: "Повторить сохранённую операцию", exact: true }); await retry.waitFor({ timeout: 20000 });
    await approver.page.screenshot({ path: `${OUT}/t3_writeoff_unknown_result.png` });
    const response = approver.page.waitForResponse((r) => r.url().endsWith("/tare/writeoff") && r.request().method() === "POST");
    await retry.click(); const r = await response; log("writeoff_retry", { status: r.status(), request: r.request().postDataJSON(), result: await r.json() });
    await status(approver.panel, "Списание проведено");
  }
  ap = await cases(approver); log("final_case", { step: ap.step, card: (await ap.card.innerText()).replace(/\s+/g, " ") });
  await ap.card.screenshot({ path: `${OUT}/t4_case_written_off_desktop.png` });
  await approver.panel.locator(".tare-balances summary").click(); await approver.panel.getByRole("button", { name: "Обновить баланс тары", exact: true }).click(); await approver.page.waitForTimeout(1200);
  log("final_balance_ui", { text: (await approver.panel.locator(".tare-balances").innerText()).replace(/\s+/g, " ") });
  await approver.panel.locator(".tare-balances").screenshot({ path: `${OUT}/t5_balance_desktop.png` });
  const mobile = await cases(admin); await mobile.card.scrollIntoViewIfNeeded(); await admin.page.screenshot({ path: `${OUT}/t6_case_mobile.png` });
  log("mobile_overflow", { overflow: await admin.page.evaluate(() => document.documentElement.scrollWidth - innerWidth) });
  log("errors", { errors }); save(); await browser.close();
})().catch((e) => { errors.push(String(e && e.stack || e).slice(0, 1500)); save(); console.error(String(e && e.stack || e).slice(0, 1500)); process.exit(1); });
