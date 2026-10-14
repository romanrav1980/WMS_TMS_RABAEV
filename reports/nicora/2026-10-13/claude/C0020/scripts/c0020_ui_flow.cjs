// C-0020: недостача 1 GOOD-единицы собственного магазина → переход в реестр недостач → независимый REJECT.
// Учётные данные — через stdin, не выводятся. Шаги идемпотентны: при повторном запуске открытое заявление
// DEV.C0020.LOSS-1 не создаётся заново, а решённое не решается повторно.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const [OUT, , EXISTING] = process.argv.slice(2); // EXISTING: уже созданное открытое заявление DEV.C0020.LOSS-1
const ctx = JSON.parse(fs.readFileSync("C:/projects/TMS/tmp/context1348.json", "utf8"));
const LOSS_REF = "DEV.C0020.LOSS-1", REJECT_REF = "DEV.C0020.REJECT-1";
const facts = [], errors = [];
const log = (name, data) => { facts.push({ name, ...data }); console.log(JSON.stringify({ name, ...data }).slice(0, 900)); };
const save = () => fs.writeFileSync(`${OUT}/../c0020_ui_facts.json`, JSON.stringify({ facts, errors }, null, 1));

(async () => {
  let input = ""; for await (const part of process.stdin) input += part; const creds = JSON.parse(input);
  const browser = await chromium.launch();
  // 1. Заявление магазина в существующей форме TarePanel.
  const page = await browser.newPage({ viewport: { width: 430, height: 940 } }); page.on("pageerror", (e) => errors.push("react: " + e.message));
  await page.goto("http://127.0.0.1:3000/?page=driver&driver_id=10018");
  await page.getByLabel("Пользователь", { exact: true }).fill(creds.driver.username); await page.getByLabel("Пароль", { exact: true }).fill(creds.driver.password);
  await page.getByRole("button", { name: "Войти", exact: true }).click();
  await page.locator("input[type=date]").fill("2026-11-03"); await page.getByText("Рейс #33571", { exact: true }).click(); await page.getByRole("button", { name: "📦 Адреса", exact: true }).click();
  const panel = page.locator(".tare-workspace");
  await panel.getByLabel("Учётная запись", { exact: true }).fill(creds.store.username); await panel.getByLabel("Пароль", { exact: true }).fill(creds.store.password);
  await panel.getByRole("button", { name: "Показать передачи этого рейса", exact: true }).click(); await panel.locator(".tare-history").waitFor();
  await panel.getByLabel("Склад-владелец", { exact: true }).selectOption(String(ctx.warehouse)); await panel.getByLabel("Тип тары", { exact: true }).selectOption(String(ctx.type));
  const form = panel.locator("fieldset").filter({ hasText: "Недостача тары у автомобиля или магазина" });
  await form.getByRole("button", { name: "Показать текущую ответственность", exact: true }).click(); await page.waitForTimeout(1200);
  const balanceOpts = await form.getByLabel("Место и состояние тары", { exact: true }).locator("option").evaluateAll((os) => os.map((o) => ({ v: o.value, t: o.textContent })));
  log("loss_balances", { options: balanceOpts });
  const storeOpt = balanceOpts.find((o) => o.t.startsWith("STORE") && /GOOD · [1-9]/.test(o.t));
  let claimOp = EXISTING || null;
  if (storeOpt && !claimOp) {
    await form.getByLabel("Место и состояние тары", { exact: true }).selectOption(storeOpt.v);
    const claimSel = form.getByLabel("Исходная выдача или акт повреждения", { exact: true });
    const claimOpts = await claimSel.locator("option").evaluateAll((os) => os.map((o) => ({ v: o.value, t: o.textContent })).filter((o) => o.v));
    log("source_claims", { options: claimOpts });
    await claimSel.selectOption(claimOpts[0].v);
    await form.getByLabel("Не обнаружено единиц", { exact: true }).fill("1"); await form.getByLabel("Обстоятельства", { exact: true }).fill("Own C0020 dev: one pallet not found at store during count");
    await form.getByLabel("Номер акта", { exact: true }).fill(LOSS_REF);
    const resp = page.waitForResponse((r) => r.url().endsWith("/api/inventory/tare/loss-report") && r.request().method() === "POST");
    await form.getByRole("button", { name: "Заявить недостачу", exact: true }).click(); const r = await resp; const body = await r.json();
    log("/loss-report", { status: r.status(), request: r.request().postDataJSON(), result: body }); save(); if (!r.ok()) throw Error(JSON.stringify(body));
    claimOp = body.operation_id;
    await panel.locator("p[role=status].tare-status").filter({ hasText: "Недостача зарегистрирована" }).waitFor();
    const card = panel.locator("section.tare-case[aria-label='Заявление о недостаче']"); await card.waitFor();
    log("react_case_card", { text: (await card.innerText()).replace(/\s+/g, " ") }); await card.screenshot({ path: `${OUT}/l1_react_loss_case.png` });
  }
  // 2. Реестр недостач: переход по складу и ID; автор (магазин) решения не принимает.
  async function rawLogin(who, query) {
    const p = await browser.newPage({ viewport: { width: 1280, height: 950 } }); p.on("pageerror", (e) => errors.push("raw: " + e.message));
    await p.goto("http://127.0.0.1:5190/tare-loss.html" + query);
    await p.fill("#loginUser", creds[who].username); await p.fill("#loginPassword", creds[who].password);
    await p.locator("#loginPassword").evaluate((el) => el.closest("form").requestSubmit());
    await p.waitForFunction(() => !document.body.classList.contains("auth-pending"), null, { timeout: 20000 }).catch(() => {});
    return p;
  }
  log("claim_used", { claimOp, reused: !!EXISTING });
  const query = "?warehouse_id=" + ctx.warehouse + (claimOp ? "&claim_id=" + encodeURIComponent(claimOp) : "");
  const author = await rawLogin("store", query); await author.waitForTimeout(2500);
  log("author_view", { authPending: await author.evaluate(() => document.body.classList.contains("auth-pending")), message: await author.textContent("#tlMessage").catch(() => ""), decideVisible: await author.locator("#tlDecideForm").isVisible().catch(() => false) });
  await author.screenshot({ path: `${OUT}/l2_author_view.png` });
  // 3. Независимый утверждающий: карточка выбрана по ссылке → REJECT; первый ответ теряется браузером → повтор того же ID.
  const ap = await rawLogin("approver", query);
  await ap.waitForFunction((id) => !!document.querySelector('[data-claim="' + id + '"]'), claimOp, { timeout: 30000 });
  const cardSel = '[data-claim="' + claimOp + '"]';
  log("approver_deeplink", { ware: await ap.inputValue("#tlWare"), selected: await ap.inputValue("#tlClaim"), card: (await ap.locator(cardSel).innerText()).replace(/\s+/g, " "), focused: await ap.locator(cardSel).evaluate((n) => n.classList.contains("tl-case-focus")) });
  await ap.locator(cardSel).screenshot({ path: `${OUT}/l3_case_open.png` });
  const open = await ap.locator(cardSel + " button").count();
  if (open) {
    await ap.locator(cardSel).getByRole("button", { name: "Принять решение" }).click(); await ap.waitForTimeout(400);
    log("decision_prefilled", { claim: await ap.inputValue("#tlClaim"), hint: await ap.textContent("#tlDecisionHint") });
    await ap.selectOption("#tlOutcome", "REJECT"); await ap.fill("#tlDecisionReason", "Own C0020 dev: pallet found at store backroom, shortage not confirmed"); await ap.fill("#tlDecisionReference", REJECT_REF);
    await ap.route("**/api/inventory/tare/loss-decide", async (route) => { const resp = await route.fetch(); const body = await resp.json(); log("decide_lost_response", { status: resp.status(), request: route.request().postDataJSON(), result: body }); save(); await route.abort("failed"); }, { times: 1 });
    await ap.click("#tlDecide"); await ap.locator("#tlRetry").waitFor({ state: "visible", timeout: 20000 });
    log("unknown_result", { message: await ap.textContent("#tlMessage"), decideDisabled: await ap.isDisabled("#tlDecide") });
    await ap.screenshot({ path: `${OUT}/l4_unknown_result.png` });
    const resp = ap.waitForResponse((r) => r.url().endsWith("/loss-decide") && r.request().method() === "POST");
    await ap.click("#tlRetry"); const r = await resp; log("decide_retry", { status: r.status(), request: r.request().postDataJSON(), result: await r.json() });
    await ap.waitForFunction(() => /Заявление отклонено/.test(document.getElementById("tlMessage").textContent), null, { timeout: 30000 });
  }
  await ap.waitForTimeout(800);
  log("final_case", { message: await ap.textContent("#tlMessage"), card: (await ap.locator(cardSel).innerText()).replace(/\s+/g, " "), availability: (await ap.locator("#tlRows").innerText()).replace(/\s+/g, " ") });
  await ap.locator(cardSel).screenshot({ path: `${OUT}/l5_case_rejected.png` });
  log("errors", { errors }); save(); await browser.close();
})().catch((e) => { errors.push(String(e && e.stack || e).slice(0, 1500)); save(); console.error(String(e && e.stack || e).slice(0, 1500)); process.exit(1); });
