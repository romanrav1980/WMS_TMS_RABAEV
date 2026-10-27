// C-0185 LIVE UI (no mocked requests): own Vite 127.0.0.1:3023 -> API 127.0.0.1:8093. Warehouse 220793322, dock B22D1161 is BLOCKED
// by the driver before this runs. 1440 and 390: real plan attempt for the owned visit (env VISIT) -> HTTP 409 YARD_DOCK_BLOCKED,
// the C0182 operator text, and no plan for the visit in the plan list. Writes nothing on success: the server refuses.
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = "C:/projects/TMS";
const { chromium } = require(ROOT + "/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync(ROOT + "/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const VISIT = process.env.VISIT, WH = "220793322", DOCK = "B22D1161";
const local = ms => { const d = new Date(ms), p = n => String(n).padStart(2, "0"); return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`; };
const res = { kind: "LIVE_OWN_VITE_API_8093_NO_MOCK", visit: VISIT, runs: [], errors: [] };
(async () => {
  const b = await chromium.launch();
  try {
    for (const [w, h] of [[1440, 1000], [390, 844]]) {
      const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage(), run = { w, posts: [] };
      p.on("pageerror", e => res.errors.push(`${w}: ${e}`));
      p.on("response", async r => { if (r.url().includes("/yard/dock-plans") && r.request().method() === "POST")
        run.posts.push({ status: r.status(), request: JSON.parse(r.request().postData()), body: await r.json().catch(() => null) }); });
      await p.goto(`http://127.0.0.1:3023/?page=workspace&workspace=shift&warehouse_id=${WH}`);
      const l = p.locator("input[type=password]");
      if (await l.waitFor({ timeout: 15000 }).then(() => true).catch(() => false)) { await p.locator("input[autocomplete=username]").fill("admin"); await l.fill(pass); await p.locator("button[type=submit]").click(); }
      await p.locator("[data-help-id='shift.process.yard']").click();
      const plan = p.locator("[aria-label='План ворот']"); await plan.waitFor({ timeout: 40000 });
      const status = p.locator("[aria-label='Состояние ворот'] li", { hasText: `Ворота ${DOCK}` });
      await status.getByText("неисправны", { exact: true }).waitFor({ timeout: 20000 });  // the real GET shows the fault mark
      await plan.locator("[data-help-id='shift.yard.plan.save']").filter({ hasText: "Запланировать ворота" }).click();
      const form = plan.locator("form.ops-yard-plan-form");
      await form.locator("select[aria-label='Визит']").selectOption(String(VISIT));
      await form.locator("[data-help-id='shift.yard.plan.dock']").fill(DOCK);
      const start = Date.now() + 5 * 3600000; await form.locator("[data-help-id='shift.yard.plan.from']").fill(local(start));
      await form.locator("[data-help-id='shift.yard.plan.to']").fill(local(start + 3600000));
      await form.locator("button[type=submit]").click();  // real click: the server answers
      const msg = plan.locator("p[role=status]", { hasText: "неисправными" }); await msg.waitFor({ timeout: 20000 });
      run.text = await msg.innerText();
      assert.strictEqual(run.posts.length, 1); assert.strictEqual(run.posts[0].status, 409);
      assert.strictEqual(run.posts[0].body.detail.code, "YARD_DOCK_BLOCKED"); assert.strictEqual(run.posts[0].body.detail.outcome_confirmed, true);
      assert.ok(run.text.includes("План или назначение не создано"));
      await plan.locator("[data-help-id='shift.yard.plan.refresh']").click(); await p.waitForTimeout(1500);
      run.plan_rows_for_visit = await plan.locator("li", { hasText: `визит ${VISIT}` }).count(); assert.strictEqual(run.plan_rows_for_visit, 0);
      run.pending_command = await plan.getByText("не подтверждена").count(); assert.strictEqual(run.pending_command, 0);  // confirmed refusal cleared the saved command
      run.size = await p.evaluate(() => ({ viewport: innerWidth, page: document.documentElement.scrollWidth })); assert.strictEqual(run.size.page, w);
      await msg.scrollIntoViewIfNeeded(); await p.screenshot({ path: path.join(SHOTS, `blocked-plan-${w}.png`) });
      res.runs.push(run); await ctx.close();
    }
    assert.deepStrictEqual(res.errors, []); res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0185-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.runs.length);
  process.exit(res.status === "PASS" ? 0 : 1);
})();
