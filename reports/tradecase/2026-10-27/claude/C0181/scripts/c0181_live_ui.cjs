// C-0181 LIVE UI (no stub): own Vite 127.0.0.1:3023 -> current local API 127.0.0.1:8093 (live Oracle, read-only GET /api/resources/timeline).
// Shift supervisor desk, warehouses 220793322 (pickers/docks) and 226192056 (dock/vehicle), today's 24 h window, 1440 and 390.
// Checks: type switching with counts, absent types named as a source limit, resource and event selection -> card, search, scale/pan,
// source chips, every planner control has a name and a help id, no page-level horizontal scroll. Nothing is written.
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = "C:/projects/TMS";
const { chromium } = require(ROOT + "/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync(ROOT + "/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const CASES = { "220793322": { search: "B22D1161", hide: "Ворота" }, "226192056": { search: "TR27D226192056", hide: "Машины" } };
const res = { kind: "LIVE_OWN_VITE_LOCAL_API_8093_NO_STUB", runs: [], errors: [] };
(async () => {
  const b = await chromium.launch();
  try {
    for (const [wh, c] of Object.entries(CASES)) for (const [w, h] of [[1440, 1000], [390, 844]]) {
      const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage(), run = { wh, w };
      p.on("pageerror", e => res.errors.push(`${wh}/${w}: ${e}`));
      p.on("response", async r => { if (r.url().includes("/api/resources/timeline")) run.api = { status: r.status(), url: r.url().replace(/^https?:\/\/[^/]+/, "") }; });
      await p.goto(`http://127.0.0.1:3023/?page=workspace&workspace=shift&warehouse_id=${wh}`);
      const l = p.locator("input[type=password]");
      if (await l.waitFor({ timeout: 15000 }).then(() => true).catch(() => false)) { await p.locator("input[autocomplete=username]").fill("admin"); await l.fill(pass); await p.locator("button[type=submit]").click(); }
      const g = p.locator("section.rg"); await g.waitFor({ timeout: 40000 });
      const groups = () => g.locator(".rg-group").allInnerTexts();
      run.summary = await g.locator(".rg-summary").innerText();
      run.types = await g.locator("[aria-label='Типы ресурсов'] button").allInnerTexts();
      run.absent = await g.locator("p.ops-note", { hasText: "Нет в ответе источника" }).innerText().catch(() => null);
      run.sources = await p.locator("[aria-label='Источники Ганта'] .ops-chip").allInnerTexts();
      run.groups = await groups();
      assert.ok(run.absent && run.absent.includes("Ричтраки"), "reach trucks absent from the source must be named");
      // Type switching (real clicks).
      const typeBtn = g.locator("[aria-label='Типы ресурсов'] button", { hasText: c.hide });
      await typeBtn.click(); assert.ok(!(await groups()).some(x => x.startsWith(c.hide)), "hidden type still shown");
      await typeBtn.click(); assert.ok((await groups()).some(x => x.startsWith(c.hide)), "type not restored");
      // Resource selection -> card.
      await g.locator("button.rg-label").first().click();
      await p.locator("section.ops-card[aria-label^='Ресурс ']").waitFor({ timeout: 10000 });
      run.resource_card = await p.locator("section.ops-card[aria-label^='Ресурс '] h3").first().innerText();
      // Event selection -> card (a bar on the axis, otherwise the queue).
      const bar = g.locator("button.rg-bar").first(), queued = g.locator(".rg-queue li button").first();
      const target = await bar.count() ? bar : await queued.count() ? queued : null;
      if (target) { run.event_from = await bar.count() ? "bar" : "queue"; await target.click({ force: true });
        await p.locator("section.ops-card[aria-label^='Работа ']").waitFor({ timeout: 10000 });
        run.event_card = await p.locator("section.ops-card[aria-label^='Работа '] h3").first().innerText(); }
      run.queue = await g.locator(".rg-queue li").allInnerTexts();
      run.row_labels = await g.locator("button.rg-label").allInnerTexts();
      if (wh === "220793322") {  // three CONTROLLED tasks started 21-22.10 without a finish: not on the axis, but findable in the queue
        assert.strictEqual(run.event_from, "queue"); assert.ok(run.queue.filter(x => x.includes("начата до окна")).length === 3, run.queue);
        assert.ok(run.row_labels.filter(x => x.includes("RESOURCE:")).length === 6, "duplicate picker labels must be told apart");
      }
      // Search.
      await g.locator("input[type=search]").fill(c.search);
      run.search_rows = await g.locator("button.rg-label").count(); assert.strictEqual(run.search_rows, 1);
      await g.locator("input[type=search]").fill("");
      // Scale and pan.
      await g.locator("[aria-label='Масштаб'] button", { hasText: "4 ч" }).click();
      const later = g.locator("button[aria-label='Позже']"); assert.strictEqual(await later.isDisabled(), false); await later.click();
      run.axis_after_pan = await g.locator(".rg-axis .rg-track").getAttribute("aria-label");
      await g.locator("[aria-label='Масштаб'] button", { hasText: "всё окно" }).click();
      // Names and help ids of every planner control; page-level overflow.
      run.audit = await p.evaluate(() => { const root = document.querySelector(".rg-planner"); const ctl = [...root.querySelectorAll("button,input,select")];
        const bad = ctl.filter(e => { const name = (e.getAttribute("aria-label") || e.textContent || "").trim() || (e.closest("label")?.textContent || "").trim();
          return !name || (!e.getAttribute("data-help-id") && !e.closest("[data-help-id]")); }).map(e => e.outerHTML.slice(0, 120));
        return { controls: ctl.length, bad, viewport: innerWidth, page: document.documentElement.scrollWidth }; });
      assert.deepStrictEqual(run.audit.bad, []); assert.strictEqual(run.audit.page, w);
      await g.scrollIntoViewIfNeeded(); await p.screenshot({ path: path.join(SHOTS, `gantt-${wh}-${w}.png`) });
      res.runs.push(run); await ctx.close();
    }
    assert.deepStrictEqual(res.errors, []); res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0181-live-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.runs.length);
  process.exit(res.status === "PASS" ? 0 : 1);
})();
