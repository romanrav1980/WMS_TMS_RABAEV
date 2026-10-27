// C-0172: own Vite preview (127.0.0.1:3021, current sources) over the real API 8088, GET only, at 1440 and 390.
// Bound trade trip of a retired own fixture (222385707 / R1.641560), read only. Three states of the trip's source time zone:
// REAL time-context (no approval) -> no calculation; STUB approval zone -> real delivery-windows in that zone; STUB mixed store zone -> limitation.
// The STUB cases change only the time-context response in the browser; every non-GET request is aborted and recorded.
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = "C:/projects/TMS";
const { chromium } = require(ROOT + "/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots");
const pass = fs.readFileSync(ROOT + "/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const WH = "222385707", TRIP = "R1.641560";
const res = { kind: "OWN_PREVIEW_REAL_API_GET_ONLY", preview: "http://127.0.0.1:3021", warehouse: WH, trip: TRIP, checks: [], writes: [], errors: [], windowsRequests: [] };
(async () => {
  const b = await chromium.launch();
  try {
    for (const mode of ["REAL", "STUB_APPROVAL", "STUB_MIXED"]) for (const w of [1440, 390]) {
      const ctx = await b.newContext({ viewport: { width: w, height: w === 390 ? 844 : 1000 } }), p = await ctx.newPage();
      p.on("pageerror", e => res.errors.push(mode + " " + w + ": " + e));
      await ctx.route("**/api/**", async r => {
        const req = r.request(), url = req.url(), m = req.method();
        if (!["GET", "OPTIONS"].includes(m) && !url.includes("/auth/")) { res.writes.push(m + " " + url); return r.abort(); }
        if (url.includes("/delivery-windows")) res.windowsRequests.push({ mode, w, url });
        if (mode !== "REAL" && m === "GET" && url.includes("/time-context")) {
          const real = await (await r.fetch()).json();
          real.last_approval = { time_zone: "Europe/Moscow", actor: "STUB", reason: "STUB" };
          real.source = real.source || {};
          real.source.store_window_profiles = mode === "STUB_MIXED" ? [{ address: "STUB", time_zone: "Asia/Tbilisi", profile_absent: false }] : [];
          return r.fulfill({ json: real });
        }
        return r.continue();
      });
      await p.goto(`http://127.0.0.1:3021/?page=tradecase&tc_wh=${WH}&tc_tab=TRIP`);
      const login = p.locator("input[type=password]");
      await Promise.race([login.waitFor({ timeout: 30000 }), p.locator(".tc-body .tc-table tbody tr").first().waitFor({ timeout: 30000 })]);
      if (await login.count()) { await p.locator("input[autocomplete=username]").fill("admin"); await login.fill(pass); await p.locator("button[type=submit]").click(); }
      await p.locator(".tc-body .tc-table tbody tr", { hasText: TRIP }).first().getByRole("button", { name: "Открыть", exact: true }).click({ timeout: 30000 });
      const plan = p.locator("[aria-label='План маршрута']");
      await plan.waitFor({ timeout: 30000 });
      const note = plan.locator("[data-help-id='tradecase.route.zone']");
      await note.first().waitFor({ timeout: 30000 });
      const text = await note.first().innerText();
      if (mode === "REAL") assert(/не подтверждён/.test(text), text);
      if (mode === "STUB_MIXED") assert(/другом поясе/.test(text), text);
      if (mode === "STUB_APPROVAL") {
        assert(/Europe\/Moscow/.test(text), text);
        await plan.locator("[role=status], [role=alert]").first().waitFor({ timeout: 30000 });
      }
      await p.waitForTimeout(1500);
      const own = res.windowsRequests.filter(x => x.mode === mode && x.w === w);
      if (mode === "STUB_APPROVAL") assert(own.length > 0 && own.every(x => x.url.includes("time_zone=Europe%2FMoscow")), JSON.stringify(own));
      else assert.strictEqual(own.length, 0, "no calculation without a confirmed source zone");
      const shown = (await plan.innerText()).slice(0, 600);
      const size = await p.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
      assert(size.document <= size.viewport + 1, JSON.stringify(size));
      await plan.scrollIntoViewIfNeeded();
      await p.screenshot({ path: path.join(SHOTS, `route-zone-${mode.toLowerCase()}-${w}.png`), fullPage: false });
      res.checks.push({ mode, width: w, note: text, windows_requests: own.length, size, shown });
      console.log("PASS", mode, w);
      await ctx.close();
    }
    assert.deepStrictEqual(res.writes, []); assert.deepStrictEqual(res.errors, []); res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0172-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length);
  process.exit(res.status === "PASS" ? 0 : 1);
})();
