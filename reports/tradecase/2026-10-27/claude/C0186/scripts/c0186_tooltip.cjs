// C-0186 regression: a real HelpButton hint stays inside the viewport. Own Vite 127.0.0.1:3023 -> API 8093, GET only (no writes).
// Shift desk -> yard of 220793322; buttons near the left ("Обновить план") and right edges; widths 320/390/768/1440; hover and keyboard
// focus; Escape hides; aria-describedby -> tooltip; title kept; no page-level horizontal scroll. argv[2]: before | after (after asserts).
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = "C:/projects/TMS";
const { chromium } = require(ROOT + "/admin/wms_admin_frontend/node_modules/playwright");
const LABEL = process.argv[2] || "after", STRICT = LABEL === "after";
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync(ROOT + "/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const TARGETS = ["shift.yard.plan.refresh", "shift.yard.dock.block", "shift.yard.refresh", "shift.yard.dock.refresh"];
const res = { label: LABEL, runs: [], errors: [] };
async function measure(p, btn) {
  return btn.evaluate(b => { const t = document.getElementById(b.getAttribute("aria-describedby")); const r = t.getBoundingClientRect(), s = getComputedStyle(t);
    return { shown: s.display !== "none", left: Math.round(r.left), right: Math.round(r.right), top: Math.round(r.top), bottom: Math.round(r.bottom),
      vw: innerWidth, vh: innerHeight, role: t.getAttribute("role"), title: b.getAttribute("title"), text: t.textContent.slice(0, 60) }; });
}
(async () => {
  const b = await chromium.launch();
  try {
    for (const w of [320, 390, 768, 1440]) {
      const ctx = await b.newContext({ viewport: { width: w, height: 900 } }), p = await ctx.newPage();
      p.on("pageerror", e => res.errors.push(`${w}: ${e}`));
      await p.goto("http://127.0.0.1:3023/?page=workspace&workspace=shift&warehouse_id=220793322");
      const l = p.locator("input[type=password]");
      if (await l.waitFor({ timeout: 15000 }).then(() => true).catch(() => false)) { await p.locator("input[autocomplete=username]").fill("admin"); await l.fill(pass); await p.locator("button[type=submit]").click(); }
      await p.locator("[data-help-id='shift.process.yard']").click();
      await p.locator("[aria-label='Состояние ворот']").waitFor({ timeout: 40000 });
      for (const id of TARGETS) {
        const btn = p.locator(`button[data-help-id='${id}']:visible`).first(); await btn.scrollIntoViewIfNeeded();
        const box = await btn.boundingBox();
        await btn.hover(); await p.waitForTimeout(150); const hover = await measure(p, btn);
        await p.mouse.move(1, 1); await btn.focus(); await p.waitForTimeout(150); const focus = await measure(p, btn);
        await p.keyboard.press("Escape"); await p.waitForTimeout(100); const escape = await measure(p, btn);
        const inside = m => m.shown && m.left >= 0 && m.right <= m.vw && m.top >= 0 && m.bottom <= m.vh;
        const row = { w, id, button: { left: Math.round(box.x), right: Math.round(box.x + box.width) }, hover, focus, escape_hidden: !escape.shown,
          hover_inside: inside(hover), focus_inside: inside(focus) };
        res.runs.push(row);
        if (id === TARGETS[0]) { await btn.hover(); await p.waitForTimeout(150); await p.screenshot({ path: path.join(SHOTS, `${LABEL}-${w}.png`) }); }
        if (STRICT) { assert.ok(row.hover_inside && row.focus_inside, JSON.stringify(row)); assert.ok(row.escape_hidden); assert.strictEqual(hover.role, "tooltip"); assert.ok(hover.title); }
      }
      // Top edge: the button scrolled to the very top of the window -> the hint flips below it instead of leaving the screen.
      const top = p.locator("button[data-help-id='shift.yard.plan.refresh']:visible").first();
      await top.evaluate(el => window.scrollBy(0, el.getBoundingClientRect().top - 4)); await p.mouse.move(1, 1); await p.waitForTimeout(100);
      await top.hover(); await p.waitForTimeout(150); const flip = await measure(p, top), tb = await top.boundingBox();
      const flipRow = { w, id: "top-edge:shift.yard.plan.refresh", button: { top: Math.round(tb.y), bottom: Math.round(tb.y + tb.height) }, hover: flip, focus: flip,
        hover_inside: flip.shown && flip.left >= 0 && flip.right <= flip.vw && flip.top >= 0 && flip.bottom <= flip.vh, below: flip.top >= Math.round(tb.y + tb.height) };
      flipRow.focus_inside = flipRow.hover_inside; res.runs.push(flipRow);
      if (STRICT) assert.ok(flipRow.hover_inside && flipRow.below, JSON.stringify(flipRow));
      const size = await p.evaluate(() => ({ viewport: innerWidth, page: document.documentElement.scrollWidth }));
      res.runs.push({ w, size }); if (STRICT) assert.strictEqual(size.page, w);
      await ctx.close();
    }
    if (STRICT) assert.deepStrictEqual(res.errors, []);
    res.status = STRICT ? "PASS" : "RECORDED";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, `c0186-tooltip-${LABEL}.json`), JSON.stringify(res, null, 1));
  const bad = res.runs.filter(r => r.id && !(r.hover_inside && r.focus_inside)).map(r => `${r.w}:${r.id}:${r.hover.left}..${r.hover.right}/${r.hover.top}`);
  console.log(res.status, "outside:", bad.join(" ") || "none");
  process.exit(res.status === "FAIL" ? 1 : 0);
})();
