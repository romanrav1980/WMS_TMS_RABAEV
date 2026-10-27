// C-0176 LIVE UI (no stub): own Vite preview 127.0.0.1:3021 over the served API 8088 after API_READY; own fixture trip (ui-fixture.json).
// 1440: real removal of 1 place whose reply is lost in the browser AFTER the server executed it (route.fetch then abort), page reload,
// the saved command is retried and gets the stored receipt. 390: real click on the visible ST button, real removal of 1 place.
// Own identity without the dispatcher right: real 403 on the places read. Root trip 33698 is not opened.
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = "C:/projects/TMS";
const { chromium } = require(ROOT + "/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const F = JSON.parse(fs.readFileSync(ROOT + "/runtime/test-evidence/tradecase/2026-10-27/C0176/ui-fixture.json", "utf8"));
const pass = fs.readFileSync(ROOT + "/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const res = { kind: "LIVE_OWN_PREVIEW_SERVED_API_NO_STUB", trip: F.trip, st: F.st, checks: [], posts: [], errors: [] };
async function login(p, user, password) {
  await p.goto(`http://127.0.0.1:3021/?page=transport&task_id=${F.trip}`);
  const l = p.locator("input[type=password]");
  if (await l.waitFor({ timeout: 15000 }).then(() => true).catch(() => false)) {
    await p.locator("input[autocomplete=username]").fill(user); await l.fill(password); await p.locator("button[type=submit]").click();
  }
}
async function openPlaces(p, w) {
  const button = p.locator(`tr:has-text("${F.st}") button.dispatch-pallet-btn:visible`).first();
  await button.waitFor({ timeout: 40000 });
  await button.click();  // a real click on the visible button at every width
  const box = p.locator(`[aria-label='Места сборки ${F.st}']`); await box.waitFor({ timeout: 20000 });
  return box;
}
async function onTrip(p) {
  return p.evaluate(async ([trip, st]) => {
    const r = await fetch(`http://127.0.0.1:8088/api/transport/trips/${trip}/sts/${encodeURIComponent(st)}/places`, { headers: { Authorization: document.cookie ? "" : "" } });
    return r.status;
  }, [F.trip, F.st]);
}
(async () => {
  const b = await chromium.launch();
  try {
    // 1440: lost reply after the server executed the removal, reload, retry -> stored receipt.
    let ctx = await b.newContext({ viewport: { width: 1440, height: 1000 } }), p = await ctx.newPage();
    p.on("pageerror", e => res.errors.push("1440: " + e));
    let lose = true;
    await ctx.route("**/place-removals", async r => {
      res.posts.push({ w: 1440, body: JSON.parse(r.request().postData()), lost: lose });
      if (lose) { const answer = await r.fetch(); res.lost_reply_status = answer.status(); lose = false; return r.abort(); }
      return r.continue();
    });
    await login(p, "admin", pass);
    let box = await openPlaces(p, 1440);
    await box.getByText(`В рейсе ${F.members.length} из ${F.members.length} мест`).waitFor();
    res.checks.push({ w: 1440, case: "live places of the own assembly" });
    await box.locator("label", { hasText: "Количество мест" }).locator("input").fill("1");
    await box.locator("label", { hasText: "Основание" }).locator("input").fill("Reduced trip, one place stays at the warehouse");
    await box.locator("[data-help-id='transport.places.prepare']").click();
    await box.locator("[data-help-id='transport.places.confirm']").click();
    await box.getByText("Результат неизвестен").waitFor({ timeout: 15000 });
    assert.strictEqual(res.lost_reply_status, 200);
    res.checks.push({ w: 1440, case: "server executed the removal, the reply was lost: unknown outcome, command kept" });
    await p.reload(); await login(p, "admin", pass); box = await openPlaces(p, 1440);  // the session is in memory, the saved command in localStorage
    await box.locator("[data-help-id='transport.places.retry']").waitFor({ timeout: 20000 });
    await p.screenshot({ path: path.join(SHOTS, "live-retry-1440.png") });
    await box.locator("[data-help-id='transport.places.retry']").click();
    await box.getByText("Снято мест: 1").waitFor({ timeout: 15000 });
    const sent = res.posts.filter(x => x.w === 1440); assert.strictEqual(sent.length, 2); assert.deepStrictEqual(sent[0].body, sent[1].body);
    await box.getByText(`В рейсе ${F.members.length - 1} из ${F.members.length} мест`).waitFor({ timeout: 15000 });
    res.checks.push({ w: 1440, case: "after reload the same command was retried and returned the stored receipt; 1 place removed once" });
    await p.screenshot({ path: path.join(SHOTS, "live-done-1440.png") });
    await ctx.close();
    // 390: real click on the visible button and a real removal of one more place.
    ctx = await b.newContext({ viewport: { width: 390, height: 844 } }); p = await ctx.newPage();
    p.on("pageerror", e => res.errors.push("390: " + e));
    await login(p, "admin", pass);
    box = await openPlaces(p, 390);
    res.checks.push({ w: 390, case: "real click on the visible ST button opened the places (no overlap)" });
    await box.locator("label", { hasText: "Количество мест" }).locator("input").fill("1");
    await box.locator("label", { hasText: "Основание" }).locator("input").fill("Second place stays at the warehouse");
    await box.locator("[data-help-id='transport.places.prepare']").click();
    await box.locator("[data-help-id='transport.places.confirm']").click();
    await box.getByText("Снято мест: 1").waitFor({ timeout: 15000 });
    await box.getByText(`В рейсе ${F.members.length - 2} из ${F.members.length} мест`).waitFor({ timeout: 15000 });
    const size = await p.evaluate(() => ({ viewport: innerWidth, page: document.documentElement.scrollWidth }));
    res.checks.push({ w: 390, case: "real removal on the phone", size });
    await box.scrollIntoViewIfNeeded(); await p.screenshot({ path: path.join(SHOTS, "live-done-390.png") });
    // Help: the registered article opens from the help button.
    await box.locator("[data-help-id='transport.places.guide']").click();
    await p.getByText("Снять часть мест сборки с рейса").first().waitFor({ timeout: 15000 });
    res.checks.push({ w: 390, case: "help button opened the published article trip-place-removal" });
    await ctx.close();
    // Real 403: own identity without the dispatcher right.
    ctx = await b.newContext({ viewport: { width: 1440, height: 1000 } }); p = await ctx.newPage();
    await login(p, F.denied_actor, F.denied_password);
    await p.waitForTimeout(4000);
    const denied = await p.evaluate(async ([trip, st, user, password]) => {
      const auth = "Basic " + btoa(user + ":" + password);
      const r = await fetch(`http://127.0.0.1:8088/api/transport/trips/${trip}/sts/${encodeURIComponent(st)}/places`, { headers: { Authorization: auth } });
      return { status: r.status, body: await r.json().catch(() => null) };
    }, [F.trip, F.st, F.denied_actor, F.denied_password]);
    res.denied = denied; assert.strictEqual(denied.status, 403);
    res.checks.push({ w: 1440, case: "own identity without the dispatcher right: places read refused 403" });
    await ctx.close();
    assert.deepStrictEqual(res.errors, []); res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0176-live-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length);
  process.exit(res.status === "PASS" ? 0 : 1);
})();
