// C-0189 UI check of the mounted static CASE picker (case-pick-tsd.html) with manual NET kg. Every API call is intercepted
// (Playwright route on the page's API base); nothing reaches a real API or Oracle. Served by a local static server on 3031.
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = "C:/projects/TMS";
const { chromium } = require(ROOT + "/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const PAGE = "http://127.0.0.1:3031/case-pick-tsd.html?case_task_id=500", API = "http://127.0.0.1:8088";
const TASK = { case_pick_task_id: 500, status: "IN_PROGRESS", wave_pick_released_at: "2026-10-28T00:00:00Z", started_at: "2026-10-28T00:05:00Z",
  tare: { booking_operation_id: "TARE-1" }, sscc: "146000000000000123", ware_id: 1, customer_name: "QA магазин", order_no: "Q-1", assigned_to: "picker",
  lines: [{ case_pick_line_id: 700, cell_code: "A-01", articul: "ART-7", product_name: "Сыр весовой", picked_qty: "1.5", planned_qty: "5" }] };
const POLICY = {
  loose: { article: "ART-7", marking_required: false, profiles: [], serialized_weight_boxes: false, weighted_kg: true, loose_weight_kg: true },
  marked: { article: "ART-7", marking_required: true, profiles: [{ system_code: "CHZ", profile_code: "UNIT" }], serialized_weight_boxes: false, weighted_kg: true, loose_weight_kg: false },
  each: { article: "ART-7", marking_required: false, profiles: [], serialized_weight_boxes: false, weighted_kg: false, loose_weight_kg: false } };
const res = { kind: "INTERCEPTED_API_ONLY_NO_LIVE_WRITE", scenarios: [], errors: [] };

async function open(b, w, policy, answers) {
  const ctx = await b.newContext({ viewport: { width: w, height: 900 } });
  await ctx.addInitScript(() => sessionStorage.setItem("wmsAdminAuth", JSON.stringify({ apiBase: "http://127.0.0.1:8088", basic: "Basic cGlja2VyOnF3ZQ==" })));
  const log = { posts: [], confirms: 0 };
  await ctx.route(API + "/**", async route => {
    const req = route.request(), url = new URL(req.url()), p = url.pathname;
    const json = (status, body) => route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
    if (p === "/api/admin/auth/me" || p === "/api/admin/auth/login") return json(200, { username: "picker", display_name: "Picker", permissions: ["case_pick_execute", "case_pick_view"] });
    if (p === "/api/case-pick/tasks/500" && req.method() === "GET") return json(200, TASK);
    if (p.endsWith("/marking-policy")) return json(200, policy);
    if (p.endsWith("/order-weight-preview")) return json(200, { requested_quantity: "5", picked_quantity: "1.5", tolerance_pct: "15", lower_quantity: "4.25", upper_quantity: "5.75", within_tolerance: false });
    if (req.method() === "POST") {
      const body = req.postData(); log.posts.push({ path: p, body });
      if (p.endsWith("/confirm")) log.confirms++;
      const answer = (answers.shift() || ((b) => [200, { operation_id: JSON.parse(b).operation_id, case_pick_task_id: 500, case_pick_line_id: 700, status: "APPLIED" }]))(body);
      return json(answer[0], answer[1]);
    }
    if (p.includes("captures")) return json(200, { items: [] });
    return json(200, Array.isArray([]) && p.endsWith("pallet-types") ? [] : {});
  });
  const page = await ctx.newPage(); page.on("pageerror", e => res.errors.push(`${w}: ${e}`));
  await page.goto(PAGE); await page.locator("#cpTsdMethod").filter({ hasNotText: "Читаю" }).waitFor({ timeout: 20000 });
  await page.waitForTimeout(300);
  return { ctx, page, log };
}
const ok = (b) => [200, { operation_id: JSON.parse(b).operation_id, case_pick_task_id: 500, case_pick_line_id: 700, status: "APPLIED" }];
const state = p => p.locator("#cpTsdState").innerText().catch(() => "");
async function scans(page) { await page.fill("#cpTsdScanCell", "A-01"); await page.fill("#cpTsdScanContainer", "146000000000000123"); }
const size = page => page.evaluate(() => ({ viewport: innerWidth, page: document.documentElement.scrollWidth }));

(async () => {
  const b = await chromium.launch();
  try {
    // A. Loose KG line at 360/390/1440: manual NET via keyboard Enter -> only /weigh-line-manual, no fact_qty / scale capture.
    for (const w of [360, 390, 1440]) {
      const { ctx, page, log } = await open(b, w, POLICY.loose, []);
      assert.ok(await page.locator("#cpTsdManualToggle").isVisible());
      assert.ok(await page.locator("#cpTsdFactQty").isDisabled());
      assert.strictEqual(await page.locator("a[href='/help/manual-weight.html#case-manual-net']").count(), 1);
      await scans(page); await page.check("#cpTsdManualToggle"); await page.locator("#cpTsdManualNetKg").focus();
      await page.keyboard.type("1.250");
      await page.locator("#cpTsdManualNet").scrollIntoViewIfNeeded(); await page.screenshot({ path: path.join(SHOTS, `manual-net-entry-${w}.png`) });
      await page.locator("#cpTsdManualNetKg").press("Enter");  // scanner/keyboard entry ends with Enter
      await page.waitForFunction(() => document.getElementById("cpTsdState")?.innerText.includes("введено вручную"), null, { timeout: 15000 });
      const post = log.posts[0], body = JSON.parse(post.body);
      assert.ok(post.path.endsWith("/tasks/500/lines/700/weigh-line-manual"));
      assert.deepStrictEqual(Object.keys(body).sort(), ["net_weight_kg", "operation_id", "scan_cell", "scan_container", "unit_scans"]);
      assert.strictEqual(body.net_weight_kg, "1.250"); assert.strictEqual(log.confirms, 0);
      const s = await size(page); assert.strictEqual(s.page, w);
      await page.locator("#cpTsdManualNet").scrollIntoViewIfNeeded(); await page.screenshot({ path: path.join(SHOTS, `manual-net-${w}.png`) });
      res.scenarios.push({ w, case: "loose KG: manual NET by keyboard Enter -> /weigh-line-manual only", body, state: await state(page), size: s });
      await ctx.close();
    }
    // B. Unknown outcome (503) -> command kept -> reload -> retry sends identical bytes; a changed value cannot start a new command.
    {
      const answers = [() => [503, { detail: { code: "RESULT_UNCERTAIN", outcome_confirmed: false, retry_same_operation_id: true } }]];
      const { ctx, page, log } = await open(b, 390, POLICY.loose, answers);
      await scans(page); await page.check("#cpTsdManualToggle"); await page.fill("#cpTsdManualNetKg", "0.800"); await page.click("#cpTsdConfirm");
      await page.waitForFunction(() => document.getElementById("cpTsdState")?.innerText.includes("Исход не подтверждён"), null, { timeout: 15000 });
      assert.ok(await page.locator("#cpTsdRetryPosting").isVisible());
      await page.reload(); await page.locator("#cpTsdRetryPosting").waitFor({ state: "visible", timeout: 15000 });
      await scans(page); await page.check("#cpTsdManualToggle"); await page.fill("#cpTsdManualNetKg", "0.900"); await page.click("#cpTsdConfirm");
      await page.waitForFunction(() => document.getElementById("cpTsdState")?.innerText.includes("Сначала повторите"), null, { timeout: 15000 });
      assert.strictEqual(log.posts.length, 1);  // the changed value was refused locally, nothing sent
      await page.click("#cpTsdRetryPosting");
      await page.waitForFunction(() => document.getElementById("cpTsdState")?.innerText.includes("введено вручную"), null, { timeout: 15000 });
      assert.strictEqual(log.posts.length, 2); assert.strictEqual(log.posts[0].body, log.posts[1].body); assert.strictEqual(JSON.parse(log.posts[1].body).net_weight_kg, "0.800");
      assert.ok(await page.locator("#cpTsdRetryPosting").isHidden()); assert.strictEqual(log.confirms, 0);
      await page.screenshot({ path: path.join(SHOTS, "manual-net-retry-390.png") });
      res.scenarios.push({ w: 390, case: "503 unknown -> reload -> changed value refused locally -> exact retry with identical bytes -> receipt", posts: log.posts.length });
      await ctx.close();
    }
    // C. Confirmed refusal (409 outcome_confirmed) clears the command; a body conflict (OPERATION_CONTENT_CONFLICT) keeps it.
    {
      const answers = [() => [409, { detail: { code: "WEIGHED_CASE_MANUAL_REJECTED", message: "Manual NET weight is only for a line whose base unit is KG", outcome_confirmed: true, retry_same_operation_id: false } }]];
      const { ctx, page, log } = await open(b, 360, POLICY.loose, answers);
      await scans(page); await page.check("#cpTsdManualToggle"); await page.fill("#cpTsdManualNetKg", "1"); await page.click("#cpTsdConfirm");
      await page.waitForFunction(() => document.getElementById("cpTsdState")?.innerText.length > 0 && !document.getElementById("cpTsdState").innerText.includes("Проведение"), null, { timeout: 15000 });
      const refused = await state(page);
      assert.ok(!refused.includes("Исход не подтверждён") && await page.locator("#cpTsdRetryPosting").isHidden(), refused);
      res.scenarios.push({ w: 360, case: "409 confirmed refusal: command cleared, no retry offered", state: refused });
      await ctx.close();
      const conflict = [() => [503, { detail: { code: "RESULT_UNCERTAIN", outcome_confirmed: false, retry_same_operation_id: true } }],
        () => [409, { detail: { code: "OPERATION_CONTENT_CONFLICT", outcome_confirmed: false, retry_same_operation_id: false, operation_id_conflict: true } }]];
      const second = await open(b, 360, POLICY.loose, conflict);
      await scans(second.page); await second.page.check("#cpTsdManualToggle"); await second.page.fill("#cpTsdManualNetKg", "1"); await second.page.click("#cpTsdConfirm");
      await second.page.locator("#cpTsdRetryPosting").waitFor({ state: "visible", timeout: 15000 }); await second.page.click("#cpTsdRetryPosting");
      await second.page.waitForTimeout(800);
      assert.ok(await second.page.locator("#cpTsdRetryPosting").isVisible(), "conflict must keep the saved command");
      res.scenarios.push({ w: 360, case: "409 OPERATION_CONTENT_CONFLICT after unknown: saved command kept (not shown as success)", state: await state(second.page) });
      await second.ctx.close();
    }
    // D. KG line without a scale capture and without manual NET: refused locally, no POST at all (never the generic confirm).
    {
      const { ctx, page, log } = await open(b, 1440, POLICY.loose, []);
      await scans(page); await page.click("#cpTsdConfirm"); await page.waitForTimeout(500);
      assert.strictEqual(log.posts.length, 0);
      res.scenarios.push({ w: 1440, case: "KG line without capture or manual NET: no request", state: await state(page) });
      await ctx.close();
    }
    // E. Marked KG line: manual NET forced; without codes nothing is sent; with codes -> /weigh-line-manual with unit_scans.
    {
      const { ctx, page, log } = await open(b, 390, POLICY.marked, []);
      assert.ok(await page.locator("#cpTsdManualToggle").isChecked() && await page.locator("#cpTsdManualToggle").isDisabled());
      await scans(page); await page.fill("#cpTsdManualNetKg", "0.5"); await page.click("#cpTsdConfirm"); await page.waitForTimeout(500);
      assert.strictEqual(log.posts.length, 0);
      await page.fill("#cpTsdMarking textarea", "0104600000000017215ABC"); await page.click("#cpTsdConfirm");
      await page.waitForFunction(() => document.getElementById("cpTsdState")?.innerText.includes("введено вручную"), null, { timeout: 15000 });
      const body = JSON.parse(log.posts[0].body);
      assert.ok(log.posts[0].path.endsWith("/weigh-line-manual")); assert.deepStrictEqual(body.unit_scans, [{ system_code: "CHZ", profile_code: "UNIT", code: "0104600000000017215ABC" }]);
      assert.strictEqual(log.confirms, 0);
      await page.screenshot({ path: path.join(SHOTS, "manual-net-marked-390.png") });
      res.scenarios.push({ w: 390, case: "marked KG: forced manual NET, codes required, sent with unit_scans", body });
      await ctx.close();
    }
    // F. Non-KG line: no manual block; the regular cumulative-fact confirm path is unchanged.
    {
      const { ctx, page, log } = await open(b, 1440, POLICY.each, []);
      assert.ok(await page.locator("#cpTsdManualNet").isHidden()); assert.ok(await page.locator("#cpTsdFactQty").isEnabled());
      await scans(page); await page.fill("#cpTsdFactQty", "2"); await page.click("#cpTsdConfirm");
      await page.waitForFunction(() => document.getElementById("cpTsdState")?.innerText.includes("Отбор проведён"), null, { timeout: 15000 });
      assert.ok(log.posts[0].path.endsWith("/confirm")); assert.strictEqual(JSON.parse(log.posts[0].body).fact_qty, "2");
      res.scenarios.push({ w: 1440, case: "non-KG line: manual hidden, regular /confirm unchanged" });
      await ctx.close();
    }
    assert.deepStrictEqual(res.errors, []); res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0189-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.scenarios.length, res.errors.slice(0, 3));
  process.exit(res.status === "PASS" ? 0 : 1);
})();
