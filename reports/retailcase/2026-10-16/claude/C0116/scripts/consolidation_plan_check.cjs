// C0116: экран ожидаемого состава. GET — живой API (только чтение). PUT/cancel — UI fixtures: перехват в браузере,
// на сервер не уходят (не native acceptance). Проверки: список/карточка/отменённый план, дерево корня, устаревший склад,
// потеря ответа → reload → точный повтор тех же байт → ACK; подтверждённый отказ 409 снимает команду.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "..", "screenshots");
const WH = "20220394", OTHER = "6558233";
const URL0 = `http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html?workspace=consolidation&warehouse_id=${WH}`;
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async () => {
  const b = await chromium.launch(); const res = { checks: [], realWrites: [], puts: [], errors: [] };
  const ctx = await b.newContext({ viewport: { width: 1500, height: 1100 } }); const p = await ctx.newPage();
  const fx = { mode: "abort" };
  p.on("pageerror", e => res.errors.push(String(e)));
  await p.route("**/api/consolidation-plans/**", async route => {
    const r = route.request();
    if (r.method() === "GET") return route.continue();
    res.puts.push({ method: r.method(), url: new URL(r.url()).pathname, body: r.postData() });
    if (fx.mode === "abort") return route.abort("connectionreset");
    const body = JSON.parse(r.postData()), plan = decodeURIComponent(new URL(r.url()).pathname.split("/")[3]);
    if (fx.mode === "refuse") return route.fulfill({ status: 409, json: { detail: { code: "CONSOLIDATION_VERSION_CONFLICT", operation_id: body.operation_id, outcome_confirmed: true, retry_same_operation_id: false } } });
    return route.fulfill({ status: 200, json: { operation_id: body.operation_id, plan_id: plan, version: body.expected_version + 1, status: "ACTIVE", stock_changed: false } });
  });
  p.on("request", r => { if (r.method() !== "GET" && r.url().includes(":8088/api/") && !r.url().includes("/consolidation-plans/")) res.realWrites.push(r.method() + " " + r.url()); });
  await p.goto(URL0); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  await p.waitForSelector(".ops-left .ops-list li", { timeout: 30000 });
  res.listActive = (await p.locator(".ops-left .ops-list li").allInnerTexts()).map(t => t.replace(/\s+/g, " "));
  await p.locator("[data-help-id='consolidation.filter']").selectOption("ALL"); await p.waitForTimeout(1500);
  res.listAll = await p.locator(".ops-left .ops-list li").count();
  // Карточка полного плана.
  await p.locator(".ops-left .ops-list li", { hasText: "MH16.TOP" }).getByRole("button", { name: "Открыть" }).click();
  await p.waitForSelector(".cp-view"); res.planFull = (await p.locator(".cp-view").innerText()).replace(/\s+/g, " ").slice(0, 400);
  assert(res.planFull.includes("Состав полон")); assert(res.planFull.includes("в составе")); res.checks.push("plan_full_members_in_root");
  await p.screenshot({ path: path.join(OUT, "c1_plan_desktop.png"), fullPage: true });
  await p.getByRole("button", { name: "Физическое дерево корня" }).click(); await p.waitForTimeout(300);
  res.treeIdentifier = await p.locator(".hu-tree-search input").inputValue(); assert.equal(res.treeIdentifier, "MH16.TOP:d076c19e82"); res.checks.push("plan_to_physical_tree_identifier");
  // Отменённый план.
  await p.locator(".ops-left .ops-list li", { hasText: "CM16.FUTURE" }).getByRole("button", { name: "Открыть" }).click(); await p.waitForTimeout(1500);
  res.planCancelled = (await p.locator(".cp-view").innerText()).replace(/\s+/g, " ").slice(0, 300);
  assert(res.planCancelled.includes("План отменён")); assert.equal(await p.getByRole("button", { name: "Изменить план" }).getAttribute("aria-disabled"), "true"); res.checks.push("cancelled_plan_read_only");
  // Команда: обрыв → сохранённая команда → reload → точный повтор → ACK.
  await p.locator(".ops-left .ops-list li", { hasText: "MH16.TOP" }).getByRole("button", { name: "Открыть" }).click(); await p.waitForSelector(".cp-view");
  await p.getByRole("button", { name: "Изменить план" }).click(); await p.getByLabel("Причина").fill("C0116 UI fixture: проверка повтора");
  await p.getByRole("button", { name: "Сохранить план" }).click(); await p.waitForSelector(".cp-pending", { timeout: 10000 });
  res.pendingText = (await p.locator(".cp-pending").innerText()).replace(/\s+/g, " ");
  const first = res.puts[0]; const fb = JSON.parse(first.body);
  assert.equal(first.method, "PUT"); assert.deepEqual(fb.fulfillment_ids, [191, 192]); assert.equal(fb.expected_version, 2); assert.equal(fb.warehouse_id, Number(WH));
  assert.equal(await p.getByRole("button", { name: "Новый план" }).getAttribute("aria-disabled"), "true");
  await p.reload(); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  await p.waitForSelector(".cp-pending", { timeout: 30000 }); fx.mode = "ack";
  await p.getByRole("button", { name: "Повторить ту же команду" }).click(); await p.waitForTimeout(1500);
  assert.equal(res.puts[1].body, first.body); assert.equal(res.puts[1].url, first.url); assert.equal(await p.locator(".cp-pending").count(), 0);
  res.ackNote = await p.locator(".ops-note[role=status]").first().innerText(); res.checks.push("lost_response_reload_exact_retry_ack");
  // Подтверждённый отказ (409 outcome_confirmed) снимает команду и требует перечитать план.
  fx.mode = "refuse"; await p.getByRole("button", { name: "Изменить план" }).click(); await p.getByLabel("Причина").fill("C0116 UI fixture: отказ версии");
  await p.getByRole("button", { name: "Сохранить план" }).click(); await p.waitForTimeout(1500);
  res.refusedNote = await p.locator(".ops-note[role=status]").first().innerText(); assert(res.refusedNote.includes("не применено")); assert.equal(await p.locator(".cp-pending").count(), 0);
  res.checks.push("confirmed_refusal_clears_pending");
  // Устаревший склад: ответ по WH задержан, выбран другой склад — показан только другой.
  await p.route(`**/api/consolidation-plans?warehouse_id=${WH}*`, async r => { await new Promise(x => setTimeout(x, 3000)); await r.continue(); });
  await p.locator(".rg-window input[list]").fill(WH + "0"); await p.locator(".rg-window input[list]").fill(WH); await p.waitForTimeout(200);
  await p.locator(".rg-window input[list]").fill(OTHER); await p.waitForTimeout(4500);
  res.staleWarehouse = { items: await p.locator(".ops-left .ops-list li").count(), text: await p.locator(".ops-left").innerText().then(t => t.replace(/\s+/g, " ").slice(0, 160)) };
  assert(!res.staleWarehouse.text.includes("MH16")); res.checks.push("stale_warehouse_response_ignored");
  // Mobile 390.
  const m = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage();
  await m.goto(URL0); await m.fill("input[autocomplete=username]", "admin"); await m.fill("input[type=password]", pass); await m.click("button[type=submit]");
  await m.waitForSelector(".ops-left .ops-list li", { timeout: 30000 }); await m.locator(".ops-left .ops-list li").first().getByRole("button", { name: "Открыть" }).click(); await m.waitForSelector(".cp-view");
  res.mobileOverflow = await m.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(res.mobileOverflow <= 0);
  await m.screenshot({ path: path.join(OUT, "c2_plan_390.png"), fullPage: true }); res.checks.push("mobile_390_no_overflow");
  assert.deepEqual(res.realWrites, []); assert.deepEqual(res.errors, []);
  res.status = "PASS"; res.fixtures = "GET live read-only; PUT/cancel intercepted UI fixtures (not sent to server)";
  fs.writeFileSync(path.join(__dirname, "..", "consolidation_plan_result.json"), JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
