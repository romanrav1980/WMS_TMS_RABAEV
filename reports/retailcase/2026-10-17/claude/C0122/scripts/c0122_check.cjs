// C0122: recovery передачи CASE по неизменной квитанции, мобильная страница CASE, native-навигация и гейты погрузки.
// Живой API: вход admin и GET (список, карточка, workspaces). Ответы POST передачи, квитанции и профиль scoped-пользователя —
// UI fixture (НЕ серверная приёмка). Если заданы C0122_SCOPED_USER/C0122_SCOPED_PASS, сценарий scoped входа идёт живым.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "..", "screenshots"); fs.mkdirSync(OUT, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const ADMIN = "http://127.0.0.1:8088/wms-admin/";
const NEW = "retailcase.caseHandoff:", OLD = "case.handoff:";
const res = { checks: [], fixturePosts: [], receipts: [], liveWrites: [], errors: [], dialogs: [] };
let transferMode = [], receiptMode = [], cardMode = null, listMode = null, auth = null;
const env = { user: process.env.C0122_SCOPED_USER, pass: process.env.C0122_SCOPED_PASS };

function receiptFor(task, body, patch = {}) {
  return { case_pick_task_id: task, status: "TRANSFERRED", offline_event_id: body.offline_event_id, actor: "admin", outcome_confirmed: true,
    source: "IMMUTABLE_TRANSFERRED_EVENT", request: { ...body }, ...patch };
}
async function setup(page) {
  page.on("pageerror", e => res.errors.push(page.url().replace(/^.*wms-admin\//, "") + ": " + String(e) + " " + (e.stack || "").split("\n")[1]));
  page.on("dialog", d => { res.dialogs.push(d.message()); d.accept(); });
  await page.route("**/api/**", async route => {
    const r = route.request(), u = r.url();
    if (auth && /\/api\/admin\/auth\/(login|me)$/.test(u)) return route.fulfill({ json: auth.user });
    if (auth && u.includes("/api/access/workspaces")) return route.fulfill({ json: auth.workspaces });
    const rec = u.match(/\/api\/case-pick\/tasks\/(\d+)\/transfer-receipt\?offline_event_id=([^&]+)/);
    if (rec) { const m = receiptMode.shift() || { status: 404 }; res.receipts.push({ id: decodeURIComponent(rec[2]), status: m.status || 200 });
      return route.fulfill(m.json ? { json: m.json } : { status: m.status, json: { detail: { code: "CASE_TRANSFER_RECEIPT_NOT_OBSERVED", outcome_confirmed: false } } }); }
    if (r.method() === "GET" && listMode && u.includes("/api/case-pick/tasks?")) return route.fulfill({ status: listMode, json: { detail: { message: "fixture " + listMode } } });
    if (r.method() === "GET" && cardMode && /\/api\/case-pick\/tasks\/\d+$/.test(u)) return route.fulfill({ status: cardMode, json: { detail: { message: "CASE_SCOPE_DENIED (fixture)" } } });
    if (r.method() === "GET") return route.continue();
    const m = u.match(/\/api\/case-pick\/tasks\/(\d+)\/transfer$/);
    if (!m) { res.liveWrites.push(r.method() + " " + u); return route.abort(); }
    const mode = transferMode.shift() || "abort"; res.fixturePosts.push({ mode, body: JSON.parse(r.postData()) });
    if (mode === "abort") return route.abort("connectionreset");
    if (mode === "ok") return route.fulfill({ json: { case_pick_task_id: +m[1], status: "TRANSFERRED" } });
    return route.fulfill({ status: +mode, json: { detail: { message: "CASE_TRANSFER_" + mode + " (fixture)" } } });
  });
}
const keys = (p, prefix) => p.evaluate(pr => Object.keys(localStorage).filter(k => k.startsWith(pr)).sort(), prefix);
const own = (p, task) => p.evaluate(([n, t]) => localStorage.getItem(n + caseApiBase() + ":" + wmsAdminAuth.state.user.username + ":" + t), [NEW, task]);
const status = p => p.locator("#caseHandoffDialog .ch-status").innerText();
const waitStatus = (p, re) => p.waitForFunction(s => new RegExp(s).test(document.querySelector("#caseHandoffDialog .ch-status")?.textContent || ""), re.source);
async function openDialog(p) { await p.locator("#caseTransfer").click(); await p.waitForSelector("#caseHandoffDialog[open] .ch-body"); }
async function closeDialog(p) { await p.click("#caseHandoffDialog .ch-x"); await p.waitForSelector("#caseHandoffDialog[open]", { state: "detached" }); }
async function fill(p) {
  await p.fill("[name=resource]", "990001"); await p.fill("[name=session]", "990002");
  if (await p.locator("[name=scan]").count()) await p.fill("[name=scan]", "FIXTURE-PALLET-1");
  await p.check("[name=confirm]");
}
async function login(p, user = "admin", secret = pass) { await p.fill("#loginUser", user); await p.fill("#loginPassword", secret); await p.click("#adminLoginForm button[type=submit]"); }
async function unknownIntent(p) {
  transferMode = ["abort"]; await openDialog(p); await fill(p); await p.click(".ch-actions button[type=submit]"); await waitStatus(p, /неизвестен/);
  return JSON.parse(await own(p, res.task)).body;
}

async function recovery(b) {
  const p = await (await b.newContext({ viewport: { width: 1440, height: 1000 } })).newPage(); await setup(p);
  await p.goto(ADMIN + "case-pick-management.html"); await login(p); await p.waitForSelector("#caseRows tr", { timeout: 30000 });
  res.task = await p.evaluate(() => caseState.selectedId); const task = res.task;
  await p.evaluate(() => Object.keys(localStorage).filter(k => k.includes("caseHandoff") || k.startsWith("case.handoff")).forEach(k => localStorage.removeItem(k)));
  // (1) Новый запрос: потеря ответа → точный повтор → 200 очищает только свой запрос.
  let body = await unknownIntent(p); transferMode = ["ok"]; await p.click("[data-act=retry]"); await waitStatus(p, /передано/);
  assert.deepEqual(res.fixturePosts.at(-1).body, res.fixturePosts.at(-2).body); assert.equal(await own(p, task), null);
  await closeDialog(p); res.checks.push("fresh_loss_exact_retry_ok_clears");
  // (2) Неверная квитанция при совпадающем текущем назначении остаётся неизвестной; верная точная квитанция снимает.
  body = await unknownIntent(p);
  transferMode = ["409"]; receiptMode = [{ json: receiptFor(task, body, { request: { ...body, to_resource_id: 1 } }) }];
  await p.click("[data-act=retry]"); await waitStatus(p, /не совпадает/); assert.notEqual(await own(p, task), null);
  for (const [label, patch] of [["other_id", { offline_event_id: "HANDOFF:other-0000-0000" }], ["other_actor", { actor: "someone" }],
    ["not_confirmed", { outcome_confirmed: false }], ["other_source", { source: "CURRENT_ASSIGNMENT" }], ["other_scan", { request: { ...body, scan_container: "X" } }]]) {
    receiptMode = [{ json: receiptFor(task, body, patch) }]; await p.click("[data-act=receipt]"); await waitStatus(p, /не совпадает/);
    assert.notEqual(await own(p, task), null, label); assert.equal(await p.locator(".ch-form").count(), 0, label);
  }
  const omitted = { ...body }; delete omitted.to_equipment_id; // nullable поле опущено = null
  receiptMode = [{ json: receiptFor(task, body, { request: omitted }) }]; await p.click("[data-act=receipt]"); await waitStatus(p, /подтверждает этот запрос/);
  assert.equal(await own(p, task), null); await p.waitForSelector(".ch-form"); await closeDialog(p);
  res.checks.push("wrong_receipt_stays_unknown_exact_receipt_resolves");
  // (3) После неизвестного исхода любой отказ 400/403/404/409/422 оставляет запрос; квитанции нет → не отмена.
  body = await unknownIntent(p);
  for (const code of ["400", "403", "404", "409", "422"]) {
    transferMode = [code]; receiptMode = [{ status: 404 }]; await p.click("[data-act=retry]"); await waitStatus(p, /остаётся/);
    assert.notEqual(await own(p, task), null, code); assert.deepEqual(res.fixturePosts.at(-1).body, body, code);
  }
  receiptMode = [{ status: 403 }]; await p.click("[data-act=receipt]"); await waitStatus(p, /только его автор/);
  receiptMode = [{ status: 503 }]; await p.click("[data-act=receipt]"); await waitStatus(p, /недоступна/);
  assert.notEqual(await own(p, task), null); res.checks.push("unknown_then_400_403_404_409_422_and_receipt_404_403_503_stay_pending");
  // (4) Копия для разбора не снимает запрос и не открывает новую передачу.
  await p.click("[data-act=copy]"); await waitStatus(p, /блокировка новой передачи остаются/);
  assert.notEqual(await own(p, task), null); assert.equal(await p.locator(".ch-form").count(), 0);
  assert.equal((await keys(p, NEW)).filter(k => k.includes(":copy:")).length, 1);
  await closeDialog(p); await openDialog(p); assert.equal(await p.locator(".ch-form").count(), 0); res.checks.push("copy_keeps_pending_and_block");
  receiptMode = [{ json: receiptFor(task, body) }]; await p.click("[data-act=receipt]"); await waitStatus(p, /подтверждает/); await closeDialog(p);
  // (5) Отказ на первой отправке — доказанный исход, запрос снимается.
  transferMode = ["409"]; await openDialog(p); await fill(p); await p.click(".ch-actions button[type=submit]"); await waitStatus(p, /снят/);
  assert.equal(await own(p, task), null); await closeDialog(p); res.checks.push("first_attempt_refusal_settles");
  // (6) Повреждённая запись: без формы и повтора; копия не разблокирует; квитанция извлечённого ключа снимает.
  const damagedId = "HANDOFF:dddddddd-0000-4000-8000-00000000c122";
  await p.evaluate(([n, t, id]) => localStorage.setItem(n + caseApiBase() + ":" + wmsAdminAuth.state.user.username + ":" + t, '{"task":' + t + ',"body":{"offline_event_id":"' + id + '",'), [NEW, task, damagedId]);
  await openDialog(p); assert.equal(await p.locator(".ch-form").count() + await p.locator("[data-act=retry]").count(), 0);
  await p.click("[data-act=copy]"); await waitStatus(p, /остаются/); assert.notEqual(await own(p, task), null);
  receiptMode = [{ status: 404 }]; await p.click("[data-act=receipt]"); await waitStatus(p, /пока нет/); assert.notEqual(await own(p, task), null);
  receiptMode = [{ json: { case_pick_task_id: task, status: "TRANSFERRED", offline_event_id: damagedId, actor: "admin", outcome_confirmed: true, source: "IMMUTABLE_TRANSFERRED_EVENT", request: { offline_event_id: damagedId } } }];
  await p.click("[data-act=receipt]"); await waitStatus(p, /подтверждает/); assert.equal(await own(p, task), null);
  assert.equal(res.receipts.at(-1).id, damagedId); await closeDialog(p); res.checks.push("damaged_blocked_copy_no_unlock_receipt_by_extracted_key");
  // (7) Прежний (legacy) запрос: исход неизвестен, 403 не удаляет.
  const legacy = { to_resource_id: 990011, to_resource_session_id: 990012, reason: "Подтверждённая передача из ARM комплектации",
    offline_event_id: "HANDOFF:00000000-0000-4000-8000-00000000c121", scan_container: "LEGACY-FIXTURE", expected_content_version: 0, expected_assigned_to: "x", expected_from_session_id: null };
  const legacyKey = await p.evaluate(([o, t, bd]) => { const k = o + caseApiBase() + ":" + wmsAdminAuth.state.user.username + ":" + t; localStorage.setItem(k, JSON.stringify(bd)); return k; }, [OLD, task, legacy]);
  transferMode = ["403"]; receiptMode = [{ status: 404 }]; await openDialog(p); assert.match(await p.locator(".ch-pending p").first().innerText(), /прежней версии/);
  await p.click("[data-act=retry]"); await waitStatus(p, /остаётся/); assert(await p.evaluate(k => localStorage.getItem(k) !== null, legacyKey));
  receiptMode = [{ json: receiptFor(task, legacy) }]; await p.click("[data-act=receipt]"); await waitStatus(p, /подтверждает/);
  assert(await p.evaluate(k => localStorage.getItem(k) === null, legacyKey)); await closeDialog(p); res.checks.push("legacy_unknown_403_kept_receipt_resolves");
  // (8) Отказ чтения: карточка 403 без старых данных, список 403 очищает строки.
  cardMode = 403; await openDialog(p).catch(() => {}); await waitStatus(p, /недоступна/);
  assert.equal(await p.locator("#caseHandoffDialog .ch-form, #caseHandoffDialog .ch-now").count(), 0); cardMode = null; await closeDialog(p);
  listMode = 403; await p.click("#caseRefresh");
  await p.waitForFunction(() => document.querySelectorAll("#caseRows tr").length === 0, null, { timeout: 8000 }); listMode = null;
  res.checks.push("read_failure_clears_card_and_rows");
  await p.context().close();
}

async function mobile(b) {
  const m = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage(); await setup(m);
  await m.goto(ADMIN + "case-pick-management.html"); await login(m); await m.waitForSelector("#caseRows tr", { timeout: 30000 });
  await m.evaluate(() => localStorage.setItem("case.short.decision:" + caseApiBase() + ":admin:999999", JSON.stringify({ decision: "RESTORE", operation_id: "SHORT.UI:fixture" })));
  await m.click("#caseRefresh"); await m.waitForTimeout(1500);
  res.mobile = await m.evaluate(async () => {
    const out = { overflow: [], overlap: null }, retry = document.querySelector(".case-short-retry"), h1 = document.querySelector(".case-title h1");
    const a = retry.getBoundingClientRect(), c = h1.getBoundingClientRect();
    out.retryVisible = !retry.hidden; out.overlap = !(a.bottom <= c.top || a.top >= c.bottom || a.right <= c.left || a.left >= c.right);
    for (const y of [0, 900, 1800, 2700, 3600]) { scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); out.overflow.push(document.documentElement.scrollWidth - innerWidth); }
    scrollTo(0, 0); return out;
  });
  assert(res.mobile.retryVisible && !res.mobile.overlap && res.mobile.overflow.every(x => x <= 0), JSON.stringify(res.mobile));
  await m.evaluate(() => Object.keys(localStorage).filter(k => k.startsWith("case.short.decision:")).forEach(k => localStorage.removeItem(k)));
  await m.screenshot({ path: path.join(OUT, "m1_case_390_top.png") });
  await m.locator("#caseTransfer").scrollIntoViewIfNeeded(); await m.screenshot({ path: path.join(OUT, "m2_case_390_detail.png") });
  await openDialog(m);
  res.mobileDialog = await m.evaluate(() => { const r = document.querySelector("#caseHandoffDialog").getBoundingClientRect(); return { l: r.left, r: r.right, t: r.top, b: r.bottom, vw: innerWidth, vh: innerHeight }; });
  assert(res.mobileDialog.l >= 0 && res.mobileDialog.r <= res.mobileDialog.vw && res.mobileDialog.b <= res.mobileDialog.vh);
  await m.screenshot({ path: path.join(OUT, "m3_dialog_390.png") }); await m.context().close();
  res.checks.push("case_page_390_no_overflow_retry_not_over_title_dialog_fits");
}

async function scoped(b) {
  const ws = picking => ({ username: "scoped", access_revision: 1, warehouses: [{ warehouse_id: 20902283, title: "20902283",
    capabilities: { picking, dispatch: picking, waves: false, warehouse_tasks: false, resource_timeline: false, resource_registry: false, resource_sessions: false } }], has_more: false, limit: 50, navigation_only: true });
  for (const picking of [true, false]) {
    const s = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage(); await setup(s);
    auth = env.user ? null : { user: { username: "admin", display_name: "scoped fixture", user_group: "X", permissions: ["wms_admin_login"] }, workspaces: ws(picking) };
    if (env.user && !picking) { await s.context().close(); continue; }
    await s.goto(ADMIN + "index.html?warehouse_id=20902283"); await login(s, env.user || "admin", env.pass || pass); await s.waitForTimeout(2500);
    const link = s.locator('[data-admin-nav] a[href^="case-pick-management.html"]').first();
    const nav = { hidden: await link.evaluate(e => e.hidden || getComputedStyle(e).display === "none"), href: await link.getAttribute("href") };
    const r = { nav };
    if (picking) {
      assert(!nav.hidden && nav.href === "case-pick-management.html?warehouse_id=20902283", JSON.stringify(nav));
      await link.click(); await s.waitForTimeout(3000);
      r.banner = await s.locator("#caseAccessBanner").innerText().catch(() => ""); r.warehouse = await s.locator(".resource-top-select").inputValue();
      r.listUrl = await s.evaluate(() => performance.getEntriesByType("resource").map(e => e.name).filter(n => n.includes("/api/case-pick/tasks?")).at(-1));
      assert.equal(r.warehouse, "20902283"); assert.match(r.listUrl || "", /ware_id=20902283/);
      await s.screenshot({ path: path.join(OUT, "s1_scoped_case.png") });
      await s.goto(ADMIN + "transport-loading.html"); await s.waitForTimeout(2500);
      r.departVisible = await s.locator('section[data-native-capability="dispatch"]').isVisible();
      await s.goto(ADMIN + "warehouse-hus.html"); await s.waitForTimeout(2500);
      r.husDenied = await s.locator(".access-denied").count(); r.huShipAttached = await s.locator("#huShip").count();
      r.shipSectionHidden = await s.locator("section.hu-divider").evaluate(e => e.hidden);
    } else {
      assert(nav.hidden, "shell-only login must not show CASE nav");
      await s.goto(ADMIN + "case-pick-management.html"); await s.waitForTimeout(3000);
      r.rows = await s.locator("#caseRows tr").count(); r.banner = await s.locator("#caseAccessBanner").innerText().catch(() => "");
      assert.equal(r.rows, 0);
      await s.goto(ADMIN + "transport-loading.html"); await s.waitForTimeout(2500);
      r.departVisible = await s.locator('section[data-native-capability="dispatch"]').isVisible(); assert(!r.departVisible);
      await s.goto(ADMIN + "warehouse-hus.html"); await s.waitForTimeout(2500); r.husDenied = await s.locator(".access-denied").count(); assert.equal(r.husDenied, 1);
    }
    res["scoped_" + (picking ? "picking_dispatch" : "shell_only")] = r; auth = null; await s.context().close();
  }
  assert(res.scoped_picking_dispatch.departVisible && res.scoped_picking_dispatch.husDenied === 0 && res.scoped_picking_dispatch.shipSectionHidden === false);
  res.checks.push("scoped_login_nav_case_warehouse_loading_gates" + (env.user ? "_LIVE" : "_FIXTURE"));
}

async function liveAdminNav(b) {
  const p = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage(); await setup(p);
  await p.goto(ADMIN + "index.html?warehouse_id=20902283"); await login(p); await p.waitForTimeout(2500);
  res.liveAdminNav = await p.locator('[data-admin-nav] a[href^="case-pick-management.html"]').first().evaluate(e => ({ hidden: e.hidden, href: e.getAttribute("href"), native: e.dataset.nativeCapability || null }));
  assert(!res.liveAdminNav.hidden && res.liveAdminNav.native === "picking"); await p.context().close();
  res.checks.push("live_workspaces_nav_admin");
}

(async () => {
  const b = await chromium.launch();
  await recovery(b); await mobile(b); await scoped(b); await liveAdminNav(b);
  assert.deepEqual(res.liveWrites, []); assert.deepEqual(res.errors, []);
  res.status = "PASS"; res.fixtures = "transfer POST, transfer-receipt and scoped profile/workspaces are UI fixtures" + (env.user ? " except scoped login (live)" : "") + "; live: admin login, CASE GET, /api/access/workspaces";
  fs.writeFileSync(path.join(__dirname, "..", "c0122_result.json"), JSON.stringify(res, null, 1));
  console.log(JSON.stringify({ status: res.status, checks: res.checks, mobile: res.mobile, scoped: [res.scoped_picking_dispatch, res.scoped_shell_only], liveAdminNav: res.liveAdminNav, dialogs: res.dialogs }, null, 1));
  await b.close();
})().catch(e => { console.error(e); console.error(JSON.stringify({ checks: res.checks, errors: res.errors, liveWrites: res.liveWrites, receipts: res.receipts.slice(-4) })); process.exit(1); });
