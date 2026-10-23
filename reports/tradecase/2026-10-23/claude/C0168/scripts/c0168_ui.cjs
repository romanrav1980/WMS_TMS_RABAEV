// C-0168: the SERVED receiving page (http://127.0.0.1:8088/wms-admin/receiving.html), real login, GET only, at 1440 and 390.
// Checks: no horizontal page scroll on 390, wide tables scroll inside their wrapper, the factory pallet hint is in the scan section,
// desktop keeps its two-column layout. Any non-GET request is aborted and recorded; nothing is received.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const URL_ = "http://127.0.0.1:8088/wms-admin/receiving.html";
const res = { kind: "LIVE_SERVED_GET_ONLY", url: URL_, checks: [], writes: [], errors: [] };
const ok = (w, name, extra = {}) => { res.checks.push({ width: w, name, ...extra }); console.log("PASS", w, name); };
(async () => {
  const b = await chromium.launch();
  try {
    for (const w of [1440, 390]) {
      const ctx = await b.newContext({ viewport: { width: w, height: w === 390 ? 844 : 1000 } }), p = await ctx.newPage();
      p.on("pageerror", e => res.errors.push(w + ": " + e));
      await ctx.route("**/*", r => { const m = r.request().method(); if (m !== "GET" && m !== "OPTIONS" && !r.request().url().includes("/auth/")) { res.writes.push(m + " " + r.request().url()); return r.abort(); } return r.continue(); });
      await p.goto(URL_);
      await p.locator("#loginUser").waitFor({ timeout: 20000 });
      await p.fill("#loginUser", "admin"); await p.fill("#loginPassword", pass); await p.keyboard.press("Enter");
      await p.waitForFunction(() => !document.body.classList.contains("auth-pending"), null, { timeout: 30000 });
      ok(w, "LIVE served receiving page after real login");
      const m = await p.evaluate(() => {
        const W = innerWidth, page = document.querySelector(".receiving-page");
        const scrollAnc = el => { for (let a = el.parentElement; a; a = a.parentElement) { const o = getComputedStyle(a).overflowX; if ((o === "auto" || o === "scroll") && a.getBoundingClientRect().right <= W + 2) return true; } return false; };
        const clipped = [...document.querySelectorAll("body *")].filter(el => { const r = el.getBoundingClientRect(); return r.width && r.right > W + 2 && !scrollAnc(el); }).slice(0, 10).map(el => el.tagName + "#" + el.id + "." + el.className);
        return { scroll: document.documentElement.scrollWidth - W, columns: getComputedStyle(page).gridTemplateColumns.split(" ").length, clipped,
                 hint: !!document.querySelector("#receiptMarking #receiptFactoryHint"), tables: document.querySelectorAll(".receiving-page .rights-table-wrap").length };
      });
      res.checks.push({ width: w, name: "measure", ...m });
      assert(m.hint, "factory pallet hint missing in the scan section"); ok(w, "factory pallet hint sits in the marking scan section");
      assert(m.scroll <= 1 && m.clipped.length === 0, JSON.stringify(m)); ok(w, "no horizontal page scroll; nothing clipped outside a scrolling wrapper");
      if (w === 1440) { assert.equal(m.columns, 2, "desktop keeps two columns"); ok(w, "desktop layout unchanged (two columns)"); }
      else { assert.equal(m.columns, 1); ok(w, "phone layout: one column, tables scroll inside their wrapper (" + m.tables + ")"); }
      await p.screenshot({ path: path.join(SHOTS, `receiving-${w}.png`), fullPage: false });
      await ctx.close();
    }
    assert.deepStrictEqual(res.writes, []); assert.deepStrictEqual(res.errors, []); res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0168-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.filter(c => c.name !== "measure").length, "checks");
  process.exit(res.status === "PASS" ? 0 : 1);
})();
