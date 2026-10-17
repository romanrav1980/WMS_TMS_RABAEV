// C0121: форма передачи CASE. Живой API — только вход и GET. Любой POST к API перехватывается:
// ответы передачи — UI fixture (сеть потеряна / 200 / 403 / 409), это НЕ серверная приёмка. Записей в живой сервер 0.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "..", "screenshots"); fs.mkdirSync(OUT, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const URL0 = "http://127.0.0.1:8088/wms-admin/case-pick-management.html";
const NEW = "retailcase.caseHandoff:", OLD = "case.handoff:";
const res = { checks: [], fixturePosts: [], liveWrites: [], errors: [], dialogs: [] };
let transferMode = [], cardMode = null, listMode = null, authFixture = null;

async function setup(page) {
  page.on("pageerror", e => res.errors.push(String(e)));
  page.on("dialog", d => { res.dialogs.push(d.message()); d.accept(); });
  await page.route("**/api/**", async route => {
    const r = route.request(), u = r.url();
    if (authFixture && /\/api\/admin\/auth\/(login|me)$/.test(u)) return route.fulfill({ json: authFixture.user });
    if (authFixture && u.endsWith("/api/access/me")) return route.fulfill({ status: authFixture.accessStatus || 200, json: authFixture.access });
    if (r.method() === "GET" && listMode && u.includes("/api/case-pick/tasks?")) return route.fulfill({ status: listMode, json: { detail: { message: "fixture " + listMode } } });
    if (r.method() === "GET" && cardMode && /\/api\/case-pick\/tasks\/\d+$/.test(u)) return route.fulfill({ status: cardMode, json: { detail: { message: "CASE_SCOPE_DENIED (fixture)" } } });
    if (r.method() === "GET") return route.continue();
    const m = u.match(/\/api\/case-pick\/tasks\/(\d+)\/transfer$/);
    if (!m) { res.liveWrites.push(r.method() + " " + u); return route.abort(); }
    const mode = transferMode.shift() || "abort"; res.fixturePosts.push({ mode, body: JSON.parse(r.postData()) });
    if (mode === "abort") return route.abort("connectionreset");
    if (mode === "ok") return route.fulfill({ json: { case_pick_task_id: +m[1], status: "TRANSFERRED" } });
    return route.fulfill({ status: +mode, json: { detail: { message: mode === "403" ? "CASE_TRANSFER_SCOPE_DENIED (fixture)" : "CASE_TRANSFER_CONFLICT (fixture)" } } });
  });
}
const ls = (p, prefix) => p.evaluate(pr => Object.keys(localStorage).filter(k => k.startsWith(pr)).sort(), prefix);
const status = p => p.locator("#caseHandoffDialog .ch-status").innerText();
async function openDialog(p) { await p.locator("#caseTransfer").click(); await p.waitForSelector("#caseHandoffDialog[open] .ch-body"); }
async function fill(p) {
  await p.fill("[name=resource]", "990001"); await p.fill("[name=session]", "990002");
  if (await p.locator("[name=scan]").count()) await p.fill("[name=scan]", "FIXTURE-PALLET-1");
  await p.check("[name=confirm]");
}
async function closeDialog(p) { await p.keyboard.press("Escape"); await p.waitForSelector("#caseHandoffDialog[open]", { state: "detached", timeout: 3000 }).catch(() => {}); }

(async () => {
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 1440, height: 1000 } })).newPage(); await setup(p);
  await p.goto(URL0); await p.fill("#loginUser", "admin"); await p.fill("#loginPassword", pass); await p.click("#adminLoginForm button[type=submit]");
  await p.waitForSelector("#caseRows tr", { timeout: 30000 });
  const task = await p.evaluate(() => caseState.selectedId); res.task = task;
  assert.equal(new URL(p.url()).searchParams.get("task_id"), String(task)); res.checks.push("task_id_in_url");
  await p.evaluate(() => Object.keys(localStorage).filter(k => k.includes("caseHandoff") || k.startsWith("case.handoff")).forEach(k => localStorage.removeItem(k)));
  // (1) Форма: живая карточка, подписи, title+help-id, фокус, Esc.
  await openDialog(p);
  res.card = await p.locator(".ch-now").innerText();
  res.untitled = await p.evaluate(() => [...document.querySelectorAll("#caseHandoffDialog button, #caseHandoffDialog input, #caseHandoffDialog a, #caseHandoffDialog summary")]
    .filter(e => !e.title || !e.dataset.helpId).map(e => e.outerHTML.slice(0, 60)));
  assert.deepEqual(res.untitled, []);
  res.focus = await p.evaluate(() => document.activeElement.name); assert.equal(res.focus, "resource");
  await p.click(".ch-actions button[type=submit]"); res.emptySubmit = await status(p); assert.match(res.emptySubmit, /ресурса/);
  assert.equal(await p.getAttribute("[name=resource]", "aria-invalid"), "true");
  await p.fill("[name=resource]", "990001"); await p.fill("[name=session]", "990002");
  if (await p.locator("[name=scan]").count()) { await p.focus("[name=scan]"); await p.keyboard.type("FIXTURE-PALLET-1"); await p.keyboard.press("Enter");
    res.enterMovesTo = await p.evaluate(() => document.activeElement.name); assert.equal(res.enterMovesTo, "reason"); }
  await p.click(".ch-actions button[type=submit]"); assert.match(await status(p), /физическую/); assert.equal(res.fixturePosts.length, 0);
  await closeDialog(p); assert.equal(await p.locator("#caseHandoffDialog[open]").count(), 0); res.checks.push("form_labels_titles_focus_validation_esc");
  // (2) Новый запрос: потеря ответа → точный повтор → 200 очищает только свой intent.
  await p.evaluate(() => localStorage.setItem("retailcase.caseHandoff:foreign", "keep-me"));
  transferMode = ["abort", "ok"]; await openDialog(p); await fill(p); await p.click(".ch-actions button[type=submit]");
  await p.waitForFunction(() => /неизвестен/.test(document.querySelector("#caseHandoffDialog .ch-status")?.textContent || ""));
  res.afterLoss = await ls(p, NEW); assert(res.afterLoss.some(k => k.endsWith(":" + task)) && res.afterLoss.some(k => k.endsWith(":delivery")));
  await p.click("[data-act=retry]"); await p.waitForFunction(() => /передано/.test(document.querySelector("#caseHandoffDialog .ch-status")?.textContent || ""));
  const [a1, a2] = res.fixturePosts.slice(-2); assert.deepEqual(a1.body, a2.body); assert.match(a1.body.offline_event_id, /^HANDOFF:/);
  res.exactRetryBody = a1.body; res.afterSuccess = await ls(p, NEW); assert.deepEqual(res.afterSuccess, ["retailcase.caseHandoff:foreign"]);
  await p.evaluate(() => localStorage.removeItem("retailcase.caseHandoff:foreign"));
  await closeDialog(p); res.checks.push("fresh_submit_loss_exact_retry_success_clears_own_only");
  // (3) Неизвестный исход → 409 и 403 сохраняют intent; снятие только явным подтверждением, в архив.
  transferMode = ["abort", "409", "403"]; await openDialog(p); await fill(p); await p.click(".ch-actions button[type=submit]");
  await p.waitForFunction(() => /неизвестен/.test(document.querySelector("#caseHandoffDialog .ch-status")?.textContent || ""));
  await p.click("[data-act=retry]"); await p.waitForFunction(() => /Конфликт/.test(document.querySelector("#caseHandoffDialog .ch-status")?.textContent || ""));
  res.after409 = await ls(p, NEW); assert(res.after409.some(k => k.endsWith(":" + task)));
  await p.click("[data-act=retry]"); await p.waitForFunction(() => /Нет права/.test(document.querySelector("#caseHandoffDialog .ch-status")?.textContent || ""));
  res.after403 = await ls(p, NEW); assert(res.after403.some(k => k.endsWith(":" + task)));
  assert.deepEqual(res.fixturePosts.at(-1).body, res.fixturePosts.at(-3).body);
  await p.click(".ch-resolve summary"); await p.click("[data-act=resolve]"); assert.match(await status(p), /подтвердите/i);
  await p.check("[name=resolved]"); await p.click("[data-act=resolve]"); await p.waitForSelector(".ch-form");
  res.afterResolve = await ls(p, NEW); assert(res.afterResolve.length === 1 && res.afterResolve[0].includes(":resolved:"));
  await closeDialog(p); res.checks.push("unknown_then_409_403_keeps_intent_explicit_resolve_archives");
  // (4) Отказ на первой отправке — доказанный исход, запрос снимается.
  transferMode = ["409"]; await openDialog(p); await fill(p); await p.click(".ch-actions button[type=submit]");
  await p.waitForFunction(() => /Конфликт/.test(document.querySelector("#caseHandoffDialog .ch-status")?.textContent || ""));
  res.firstRefusal = (await ls(p, NEW)).filter(k => !k.includes(":resolved:")); assert.deepEqual(res.firstRefusal, []);
  await closeDialog(p); res.checks.push("first_attempt_refusal_settles");
  // (5) Прежний (legacy) запрос: отдельная пометка, повтор тем же телом, 403 не удаляет.
  const legacyBody = { to_resource_id: 990011, to_resource_session_id: 990012, reason: "Подтверждённая передача из ARM комплектации",
    offline_event_id: "HANDOFF:00000000-0000-4000-8000-00000000c121", scan_container: "LEGACY-FIXTURE", expected_content_version: 0, expected_assigned_to: "x", expected_from_session_id: null };
  const legacyKey = await p.evaluate(([o, t, bd]) => { const k = o + caseApiBase() + ":" + wmsAdminAuth.state.user.username + ":" + t; localStorage.setItem(k, JSON.stringify(bd)); return k; }, [OLD, task, legacyBody]);
  transferMode = ["403"]; await openDialog(p); res.legacyText = await p.locator(".ch-pending p").first().innerText(); assert.match(res.legacyText, /прежней версии/);
  assert.equal(await p.locator(".ch-form").count(), 0);
  await p.click("[data-act=retry]"); await p.waitForFunction(() => /Нет права/.test(document.querySelector("#caseHandoffDialog .ch-status")?.textContent || ""));
  assert.deepEqual(res.fixturePosts.at(-1).body, legacyBody);
  res.legacyKept = await p.evaluate(k => localStorage.getItem(k) !== null, legacyKey); assert(res.legacyKept);
  await p.click(".ch-resolve summary"); await p.check("[name=resolved]"); await p.click("[data-act=resolve]"); await p.waitForSelector(".ch-form");
  await closeDialog(p); res.checks.push("legacy_intent_separate_exact_retry_403_kept");
  // (6) Повреждённый журнал не затирается: новая передача заблокирована до явного архива.
  const badKey = await p.evaluate(([n, t]) => { const k = n + caseApiBase() + ":" + wmsAdminAuth.state.user.username + ":" + t; localStorage.setItem(k, "{broken"); return k; }, [NEW, task]);
  await openDialog(p); assert.equal(await p.locator(".ch-form").count(), 0); assert.equal(await p.locator("[data-act=retry]").count(), 0);
  assert.equal(await p.evaluate(k => localStorage.getItem(k), badKey), "{broken");
  await p.click("[data-act=archive]"); await p.waitForSelector(".ch-form");
  res.damagedArchive = await p.evaluate(k => Object.keys(localStorage).filter(x => x.startsWith(k + ":damaged:")).map(x => localStorage.getItem(x)), badKey);
  assert.deepEqual(res.damagedArchive, ["{broken"]); await closeDialog(p); res.checks.push("corrupt_journal_preserved_archive_only");
  // (7) 403 карточки: отказ без прежних данных и без формы.
  cardMode = 403; await openDialog(p).catch(() => {}); await p.waitForFunction(() => /недоступна/.test(document.querySelector("#caseHandoffDialog .ch-status")?.textContent || ""));
  res.card403 = { status: await status(p), form: await p.locator(".ch-form").count(), card: await p.locator(".ch-now").count() };
  assert.equal(res.card403.form + res.card403.card, 0); cardMode = null; await closeDialog(p); res.checks.push("card_403_no_stale_data");
  await p.screenshot({ path: path.join(OUT, "h1_desktop_page.png") });
  // (8) Список 403 при обновлении очищает прежние строки.
  listMode = 403; await p.click("#caseRefresh"); await p.waitForTimeout(1200);
  res.rowsAfter403 = await p.locator("#caseRows tr").count(); assert.equal(res.rowsAfter403, 0); listMode = null; res.checks.push("list_403_clears_rows");
  // (9) Перезагрузка возвращает то же задание (task_id в адресе).
  await p.reload(); await p.waitForSelector("#caseRows tr", { timeout: 30000 }); assert.equal(await p.evaluate(() => caseState.selectedId), task); res.checks.push("reload_keeps_task");
  // (10) 390×844: окно в экране, поля ≥44 px, без горизонтальной прокрутки внутри окна; скриншот.
  const m = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage(); await setup(m);
  await m.goto(URL0 + "?task_id=" + task); await m.fill("#loginUser", "admin"); await m.fill("#loginPassword", pass); await m.click("#adminLoginForm button[type=submit]");
  await m.waitForSelector("#caseRows tr", { timeout: 30000 }); await openDialog(m);
  res.mobile = await m.evaluate(() => { const d = document.querySelector("#caseHandoffDialog"), r = d.getBoundingClientRect();
    const small = [...d.querySelectorAll("input:not([type=checkbox]), .ch-actions button, .ch-x")].filter(e => e.getBoundingClientRect().height < 44).length;
    return { left: r.left, right: r.right, top: r.top, bottom: r.bottom, vw: innerWidth, vh: innerHeight, overflowX: d.scrollWidth - d.clientWidth, small }; });
  assert(res.mobile.left >= 0 && res.mobile.right <= res.mobile.vw && res.mobile.top >= 0 && res.mobile.bottom <= res.mobile.vh && res.mobile.overflowX <= 0 && res.mobile.small === 0);
  await m.screenshot({ path: path.join(OUT, "h2_dialog_390.png") });
  await m.keyboard.press("Tab"); await m.keyboard.press("Tab"); res.mobileTab = await m.evaluate(() => document.activeElement.closest("#caseHandoffDialog") !== null); assert(res.mobileTab);
  await closeDialog(m); res.checks.push("mobile_390_dialog_fits_keyboard");
  // (11) Доступ по области (fixture профиля): без плоского права и с ACTIVE назначением — экран открыт; без назначений — отказ без данных.
  for (const [assignments, expectRows] of [[[{ assignment_state: "ACTIVE", scope_kind: "WAREHOUSE", scope_id: "20902283" }], true], [[], false]]) {
    const s = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage(); await setup(s);
    authFixture = { user: { username: "admin", display_name: "scoped fixture", user_group: "X", permissions: ["admin_login"] }, access: { username: "admin", assignments } };
    await s.goto(URL0); await s.fill("#loginUser", "admin"); await s.fill("#loginPassword", pass); await s.click("#adminLoginForm button[type=submit]"); await s.waitForTimeout(3000);
    const r = { rows: await s.locator("#caseRows tr").count(), banner: await s.locator("#caseAccessBanner").innerText().catch(() => "") };
    res["scoped_" + (expectRows ? "active" : "none")] = r; assert.equal(r.rows > 0, expectRows);
    if (expectRows) await s.screenshot({ path: path.join(OUT, "h3_scoped_banner.png") });
    authFixture = null; await s.context().close();
  }
  res.checks.push("scoped_assignment_opens_page_none_denies");
  assert.deepEqual(res.liveWrites, []); assert.deepEqual(res.errors, []);
  res.status = "PASS"; res.fixtures = "transfer POST responses and scoped profile are UI fixtures; live API used only for login and GET";
  fs.writeFileSync(path.join(__dirname, "..", "c0121_result.json"), JSON.stringify(res, null, 1)); console.log(JSON.stringify({ status: res.status, checks: res.checks, task: res.task, dialogs: res.dialogs, mobile: res.mobile, scoped: [res.scoped_active, res.scoped_none] }, null, 1));
  await b.close();
})().catch(e => { console.error(e); console.error(JSON.stringify({ checks: res.checks, errors: res.errors, liveWrites: res.liveWrites, dialogs: res.dialogs })); process.exit(1); });
