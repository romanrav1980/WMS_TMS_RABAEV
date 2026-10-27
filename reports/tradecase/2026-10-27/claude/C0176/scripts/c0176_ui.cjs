// C-0176 UI on the own Vite preview (127.0.0.1:3021, current sources) over the real API 8088; real login and the real trip 33698 read
// only. STUB: the two new endpoints (places / place-removals) are answered in the browser because the native kit is not applied yet;
// this checks the screen and the intent/retry/403 behaviour, NOT the real removal. Every other non-GET request is aborted.
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = "C:/projects/TMS";
const { chromium } = require(ROOT + "/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync(ROOT + "/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const TRIP = 33698, ST = "P210069361104", HASH = "A".repeat(64);
const res = { kind: "OWN_PREVIEW_REAL_LOGIN_REAL_TRIP_READ_ONLY_STUB_NEW_ENDPOINTS", trip: TRIP, st: ST, checks: [], writes: [], errors: [], posts: [] };
const stubPlaces = (n) => ({ trip_id: TRIP, st_number: ST, warehouse_id: 210069361, on_trip: n, source_hash: HASH,
  places: Array.from({ length: 6 }, (_, i) => ({ member_id: 900 + i, pallet_uid: "STUB.PLACE." + (i + 1), address: "STUB address", on_trip: i < n,
    other_trip: null, loaded: false, shipped: false, quantity: "10" })) });
(async () => {
  const b = await chromium.launch();
  try {
    for (const w of [1440, 390]) {
      const ctx = await b.newContext({ viewport: { width: w, height: w === 390 ? 844 : 1000 } }), p = await ctx.newPage();
      p.on("pageerror", e => res.errors.push(w + ": " + e));
      let postNo = 0, denied = false, onTrip = 6;
      await ctx.route("**/api/**", async r => {
        const req = r.request(), url = req.url(), m = req.method();
        if (url.includes(`/api/transport/trips/${TRIP}/sts/`) && url.endsWith("/places") && m === "GET")
          return denied ? r.fulfill({ status: 403, json: { detail: { code: "ACCESS_DENIED" } } }) : r.fulfill({ json: stubPlaces(onTrip) });
        if (url.endsWith(`/api/transport/trips/${TRIP}/place-removals`) && m === "POST") {
          const body = JSON.parse(req.postData()); res.posts.push({ w, body }); postNo++;
          if (postNo === 1) return r.fulfill({ status: 503, json: { detail: { code: "PLACE_REMOVAL_RESULT_UNKNOWN", outcome_confirmed: false, retry_same_operation_id: true } } });
          onTrip = 6 - body.member_ids.length;
          return r.fulfill({ json: { operation_id: body.operation_id, trip_id: TRIP, st_number: ST, removed: body.member_ids, on_trip_after: onTrip, stock_changed: false } });
        }
        if (!["GET", "OPTIONS"].includes(m) && !url.includes("/auth/")) { res.writes.push(m + " " + url); return r.abort(); }
        return r.continue();
      });
      await p.goto(`http://127.0.0.1:3021/?page=transport&task_id=${TRIP}`);
      const login = p.locator("input[type=password]");
      if (await login.count().catch(() => 0) || await login.waitFor({ timeout: 15000 }).then(() => true).catch(() => false)) {
        await p.locator("input[autocomplete=username]").fill("admin"); await login.fill(pass); await p.locator("button[type=submit]").click();
      }
      const button = p.locator(`tr:has-text("${ST}") button.dispatch-pallet-btn:visible`).first();
      await button.waitFor({ timeout: 40000 });
      if (w === 390) {  // the existing dispatch page: its right filter panel covers the ST table on a phone (observed, not changed here)
        res.checks.push({ w, case: "existing page: right panel intercepts the ST row button on 390; panel opened by a click event on the button" });
        await button.dispatchEvent("click");
      } else await button.click();
      const box = p.locator(`[aria-label='Места сборки ${ST}']`);
      await box.waitFor({ timeout: 20000 });
      await box.getByText("В рейсе 6 из 6 мест").waitFor();
      res.checks.push({ w, case: "places list of the selected assembly shown" });
      await box.locator("[data-help-id='transport.places.count'] input").fill("2");
      assert.strictEqual(await box.locator("input[type=checkbox]:checked").count(), 2);
      await box.locator("label", { hasText: "Основание" }).locator("input").fill("Reduced trip keeps 4 places");
      await box.locator("[data-help-id='transport.places.prepare']").click();
      await box.locator("[aria-label='Подтверждение снятия']").waitFor();
      await p.screenshot({ path: path.join(SHOTS, `places-confirm-${w}.png`), fullPage: false });
      await box.locator("[data-help-id='transport.places.confirm']").click();
      await box.locator("[data-help-id='transport.places.retry']").waitFor({ timeout: 10000 });
      res.checks.push({ w, case: "503 kept the saved command and offers the exact retry" });
      await box.locator("[data-help-id='transport.places.retry']").click();
      await box.getByText("Снято мест: 2").waitFor({ timeout: 10000 });
      const mine = res.posts.filter(x => x.w === w);
      assert.strictEqual(mine.length, 2); assert.deepStrictEqual(mine[0].body, mine[1].body);
      assert.deepStrictEqual(mine[0].body.member_ids, [904, 905]); assert.strictEqual(mine[0].body.expected_source_hash, HASH);
      res.checks.push({ w, case: "retry sent the identical body (same operation id and membership version); success shown" });
      const size = await p.evaluate(() => ({ viewport: innerWidth, page: document.documentElement.scrollWidth }));
      const own = await box.evaluate(el => { const r = el.getBoundingClientRect(); return { left: Math.round(r.left), right: Math.round(r.right), width: Math.round(r.width) }; });
      await box.scrollIntoViewIfNeeded(); await p.screenshot({ path: path.join(SHOTS, `places-done-${w}.png`), fullPage: false });
      res.checks.push({ w, case: "layout", size, own });
      denied = true; await box.locator("[data-help-id='transport.places.reload']").click();
      await box.getByText("Нет доступа к местам этой сборки.").waitFor({ timeout: 10000 });
      assert.strictEqual(await box.locator("table").count(), 0);
      res.checks.push({ w, case: "403 on reload clears the places" });
      await ctx.close();
    }
    assert.deepStrictEqual(res.writes, []); assert.deepStrictEqual(res.errors, []); res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0176-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length);
  process.exit(res.status === "PASS" ? 0 : 1);
})();
