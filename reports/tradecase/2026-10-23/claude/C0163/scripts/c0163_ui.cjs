// C-0163 «Состав поставок частями» во вкладке «Сообщения обмена» (dev :3021) при 1440 и 390.
// ЖИВОЕ (GET): вход и страница сообщений склада 210564699. FIXTURE: GET supply-transfers (маршрут на :8088 ещё не загружен, native
// NOT_APPLIED) и POST deliver; 403 списка. Это подставные ответы, не исход сервера. Других не-GET нет.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0163_BASE || "http://127.0.0.1:3021/", WH = 210564699;
const res = { base: BASE, checks: [], writes: [], errors: [], posts: [] };
const cors = { "access-control-allow-origin": "*" };
let fx = {};
const row = (id, status, extra = {}) => ({ warehouse_id: WH, source_id: "TC03.SAP", transfer_id: id, document_id: "SUP." + id, version: 2, part_count: 3,
  received_codes: 5, missing_parts: [], end_received: true, status, status_reason: null, owner_id: "SNS", ...extra });

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (u.includes("/supply-transfers") && m === "GET") {
    if (fx.denied) return r.fulfill({ status: 403, headers: cors, json: { detail: { code: "TRADECASE_ACCESS_DENIED" } } });
    return r.fulfill({ status: 200, headers: cors, json: { warehouse_id: WH, has_more: false, items: [
      row("T1", "OPEN", { missing_parts: [1], end_received: true, received_codes: 4 }),
      row("T2", "MISMATCH", { status_reason: "TOTAL_MISMATCH:7/8", received_codes: 7 }),
      row("T3", "COMPLETE", { received_codes: 7 }), row("T4", "DELIVERED", { received_codes: 7 })] } });
  }
  if (u.includes("/supply-transfers/") && u.endsWith("/deliver") && m === "POST") { res.posts.push(u); return r.fulfill({ status: 200, headers: cors, json: row("T3", "DELIVERED") }); }
  if (m !== "GET" && !u.includes("/auth/")) { res.writes.push(m + " " + u); return r.abort(); }
  return r.continue();
}
const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };

async function width(b, w, h) {
  fx = {}; res.posts = [];
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await ctx.route(u => u.href.includes(":8088/api/"), route);
  await p.goto(`${BASE}?page=tradecase&tc_wh=${WH}&tc_tab=MESSAGES`);
  const login = p.locator("input[type=password]"), panel = p.locator("[aria-label='Состав поставок частями']");
  await Promise.race([login.waitFor({ timeout: 30000 }), panel.waitFor({ timeout: 30000 })]);
  if (await login.count()) { await p.fill("input[autocomplete=username]", "admin"); await login.fill(pass); await p.click("button[type=submit]"); }
  await panel.getByText("SUP.T1").waitFor({ timeout: 45000 }); ok(w, "LIVE messages tab opens with the parts panel");
  const t = await panel.innerText();
  assert(/нет частей: 1/.test(t) && /состав не сходится/.test(t) && /число кодов не сходится \(получено\/заявлено 7\/8\)/.test(t) && /передан в приём/.test(t), t);
  ok(w, "FIXTURE transfers: missing part, total mismatch, delivered — in plain words");
  await panel.locator("li", { hasText: "SUP.T3" }).getByRole("button", { name: "Передать в приём" }).click();
  await panel.getByText("Состав T3 передан в приём.").waitFor(); assert(res.posts.length === 1 && res.posts[0].includes("/TC03.SAP/T3/deliver")); ok(w, "FIXTURE hand-over retry posts the same transfer once");
  await panel.locator("li", { hasText: "SUP.T4" }).getByRole("button", { name: "Открыть поставку" }).click();
  await p.waitForFunction(() => /tc_tab=SUPPLY/.test(location.search) && /tc_open=SUP\.T4/.test(location.search), null, { timeout: 15000 });
  ok(w, "delivered transfer opens the SUPPLY document in place");
  await p.goto(`${BASE}?page=tradecase&tc_wh=${WH}&tc_tab=MESSAGES`).catch(() => {});
  if (await p.locator("input[type=password]").count()) { await p.fill("input[autocomplete=username]", "admin"); await p.locator("input[type=password]").fill(pass); await p.click("button[type=submit]"); }
  await panel.getByText("SUP.T1").waitFor({ timeout: 45000 });
  const bad = await panel.locator("button").evaluateAll(bs => bs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every panel button has title and help id");
  const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(over <= 1, "overflow " + over); ok(w, "no horizontal page scroll");
  const href = await panel.locator("a[href*='help/tradecase-documents.html']").first().getAttribute("href");
  const help = await ctx.request.get(new URL(href, BASE).href); assert.equal(help.status(), 200); assert((await help.text()).includes('id="supply-parts"')); ok(w, "static help link answers 200 with the parts section");
  await panel.screenshot({ path: path.join(SHOTS, `supply-parts-${w}.png`) });
  fx.denied = true; await panel.getByRole("button", { name: "Обновить" }).click();
  await panel.getByText("Передачи не прочитаны").waitFor(); assert(await panel.locator("li").count() === 0); ok(w, "FIXTURE 403 clears the list (no stale rows)");
  await ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try { await width(b, 1440, 1000); await width(b, 390, 844); assert.deepStrictEqual(res.errors, []); assert.deepStrictEqual(res.writes, []); res.status = "PASS"; }
  catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0163-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length, "checks");
  process.exit(res.status === "PASS" ? 0 : 1);
})();
