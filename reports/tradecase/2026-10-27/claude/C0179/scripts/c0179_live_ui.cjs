// C-0179 LIVE UI (no stub): own Vite 127.0.0.1:3023 -> own API instance 127.0.0.1:8093 with the current code (C0178) and real Oracle
// (the shared 8088 still serves pre-C0178 code and is restarted only by root). Trip T1 of warehouse 226192056, product A.
// 1440 and 390: a real click on "Рассчитать место"; the reason text must match the real API blocking_reason; no new API calls.
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = "C:/projects/TMS";
const { chromium } = require(ROOT + "/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync(ROOT + "/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const URL = "http://127.0.0.1:3023/?page=tradecase&tc_wh=226192056&tc_tab=TRIP&tc_open=T1";
const res = { kind: "LIVE_OWN_VITE_OWN_API_CURRENT_CODE_NO_STUB", checks: [], capacity_calls: [], errors: [] };
(async () => {
  const b = await chromium.launch();
  try {
    for (const [w, h] of [[1440, 1000], [390, 844]]) {
      const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
      p.on("pageerror", e => res.errors.push(`${w}: ${e}`));
      p.on("response", async r => { if (r.url().includes("/capacity?")) res.capacity_calls.push({ w, status: r.status(), body: await r.json().catch(() => null) }); });
      await p.goto(URL);
      const l = p.locator("input[type=password]");
      if (await l.waitFor({ timeout: 15000 }).then(() => true).catch(() => false)) {
        await p.locator("input[autocomplete=username]").fill("admin"); await l.fill(pass); await p.locator("button[type=submit]").click();
      }
      const box = p.locator("section.tc-capacity"); await box.waitFor({ timeout: 40000 });
      await box.locator("[data-help-id='tradecase.capacity.sku']").fill("A");
      await box.locator("[data-help-id='tradecase.capacity.quantity']").fill("1");
      await box.locator("[data-help-id='tradecase.capacity.calculate']").click();  // real click on the visible button
      const msg = box.locator("p.tc-msg.warn[data-reason]"); await msg.waitFor({ timeout: 30000 });
      const api = res.capacity_calls.filter(c => c.w === w).pop();
      assert.strictEqual(api.status, 200);
      assert.strictEqual(await msg.getAttribute("data-reason"), api.body.blocking_reason);
      assert.strictEqual(api.body.blocking_reason, "TOPUP_PALLET_PLACE_MAPPING_REQUIRED");
      const text = await msg.innerText();
      assert.ok(text.includes("не настроены и не подтверждены тип паллеты") && text.includes("заказ и резерв не создаются") && text.includes("Код: TOPUP_PALLET_PLACE_MAPPING_REQUIRED"), text);
      assert.strictEqual(await box.getByText("В пределах расчёта").count(), 0);  // nothing presented as fitting
      await box.getByText("только оценка").waitFor();
      assert.ok(await box.locator("h4 a, h4 button").count() >= 1, "help link kept");
      const size = await p.evaluate(() => ({ viewport: innerWidth, page: document.documentElement.scrollWidth }));
      await box.scrollIntoViewIfNeeded(); await box.screenshot({ path: path.join(SHOTS, `capacity-reason-${w}.png`) });
      res.checks.push({ w, case: "real click; reason text matches real API blocking_reason; no fitting line; estimates labelled; help link kept", reason: api.body.blocking_reason, size, text });
      await ctx.close();
    }
    assert.strictEqual(res.capacity_calls.length, 2);
    assert.deepStrictEqual(res.errors, []); res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0179-live-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length, res.capacity_calls.length);
  process.exit(res.status === "PASS" ? 0 : 1);
})();
