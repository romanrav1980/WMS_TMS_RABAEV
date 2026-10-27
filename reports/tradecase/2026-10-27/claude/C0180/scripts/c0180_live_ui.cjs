// C-0180 LIVE UI (no stub): own Vite 127.0.0.1:3023 -> Codex's API 127.0.0.1:8093 (current tree, live Oracle; API_READY_C0180).
// QA warehouse 226192056, dock TR27D226192056. 1440: real BLOCK whose reply is lost in the browser AFTER the server executed it
// (route.fetch then abort) -> unknown outcome kept -> reload -> retry with the same bytes -> receipt. 390: real UNBLOCK. The dock is left open.
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = "C:/projects/TMS";
const { chromium } = require(ROOT + "/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync(ROOT + "/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const WH = "226192056", DOCK = "TR27D226192056";
const URL = `http://127.0.0.1:3023/?page=workspace&workspace=shift&warehouse_id=${WH}`;
const res = { kind: "LIVE_OWN_VITE_CODEX_API_8093_NO_STUB", warehouse: WH, dock: DOCK, checks: [], posts: [], gets: [], errors: [] };
async function open(p) {
  await p.goto(URL);
  const l = p.locator("input[type=password]");
  if (await l.waitFor({ timeout: 15000 }).then(() => true).catch(() => false)) {
    await p.locator("input[autocomplete=username]").fill("admin"); await l.fill(pass); await p.locator("button[type=submit]").click();
  }
  await p.locator("[data-help-id='shift.process.yard']").click();  // real click on the process
  const box = p.locator("[aria-label='Состояние ворот']"); await box.waitFor({ timeout: 40000 });
  const row = box.locator("li", { hasText: `Ворота ${DOCK}` }); await row.waitFor({ timeout: 30000 });
  return { box, row };
}
function watch(p, w) {
  p.on("pageerror", e => res.errors.push(`${w}: ${e}`));
  p.on("response", async r => { if (r.url().includes("/yard/docks") && r.request().method() === "GET") res.gets.push({ w, status: r.status(), body: await r.json().catch(() => null) }); });
}
(async () => {
  const b = await chromium.launch();
  try {
    let ctx = await b.newContext({ viewport: { width: 1440, height: 1000 } }), p = await ctx.newPage(); watch(p, 1440);
    let lose = true;
    await ctx.route("**/yard/docks/*/status", async r => {
      const body = r.request().postData(); res.posts.push({ w: 1440, body: JSON.parse(body), raw: body, lost: lose });
      if (lose) { const a = await r.fetch(); res.lost_reply = { status: a.status(), body: await a.json().catch(() => null) }; lose = false; return r.abort(); }
      return r.continue();
    });
    let { box, row } = await open(p);
    await row.getByText("исправны", { exact: true }).waitFor();
    res.checks.push({ w: 1440, case: "real GET: dock shown open" });
    await row.locator("[data-help-id='shift.yard.dock.block']").click();
    await row.locator("input[aria-label='Описание неисправности']").fill("C-0180 QA: створка не закрывается");
    await row.locator("[data-help-id='shift.yard.dock.block']").filter({ hasText: "Отметить неисправность" }).click();
    await box.getByText("не подтверждена").waitFor({ timeout: 15000 });
    assert.strictEqual(res.lost_reply.status, 200);
    res.checks.push({ w: 1440, case: "server executed BLOCK, reply lost: outcome unknown, command kept with retry" });
    await p.reload(); ({ box, row } = await open(p));
    await box.locator("[data-help-id='shift.yard.dock.retry']").waitFor({ timeout: 20000 });
    await p.screenshot({ path: path.join(SHOTS, "dock-retry-1440.png") });
    await box.locator("[data-help-id='shift.yard.dock.retry']").click();
    await box.getByText(`Выполнено: ворота ${DOCK} — отмечена неисправность.`).waitFor({ timeout: 15000 });
    await row.getByText("неисправны", { exact: true }).waitFor({ timeout: 15000 });
    await row.getByText("Причина: C-0180 QA: створка не закрывается").waitFor();
    const sent = res.posts.filter(x => x.w === 1440); assert.strictEqual(sent.length, 2); assert.strictEqual(sent[0].raw, sent[1].raw);
    res.checks.push({ w: 1440, case: "after reload the same bytes were retried; receipt accepted; GET shows blocked with reason" });
    await box.scrollIntoViewIfNeeded(); await p.screenshot({ path: path.join(SHOTS, "dock-blocked-1440.png") });
    await ctx.close();

    ctx = await b.newContext({ viewport: { width: 390, height: 844 } }); p = await ctx.newPage(); watch(p, 390);
    p.on("request", r => { if (r.url().includes("/yard/docks/") && r.method() === "POST") res.posts.push({ w: 390, body: JSON.parse(r.postData()) }); });
    ({ box, row } = await open(p));
    await row.getByText("неисправны", { exact: true }).waitFor();
    await row.locator("[data-help-id='shift.yard.dock.unblock']").click();  // real click on the visible button
    await row.locator("input[aria-label='Причина открытия']").fill("C-0180 QA: отремонтировано, проверено");
    await row.locator("[data-help-id='shift.yard.dock.unblock']").filter({ hasText: "Открыть после ремонта" }).click();
    await box.getByText(`Выполнено: ворота ${DOCK} — открыты.`).waitFor({ timeout: 15000 });
    await row.getByText("исправны", { exact: true }).waitFor({ timeout: 15000 });
    const size = await p.evaluate(() => ({ viewport: innerWidth, page: document.documentElement.scrollWidth }));
    res.checks.push({ w: 390, case: "real UNBLOCK on the phone; dock open again", size });
    await box.scrollIntoViewIfNeeded(); await p.screenshot({ path: path.join(SHOTS, "dock-open-390.png") });
    await ctx.close();
    res.unknown_rows = (res.gets.at(-1)?.body?.docks ?? []).filter(d => d.blocked === null).map(d => ({ dock: d.dock, ambiguous: d.ambiguous, status_error: d.status_error }));
    assert.deepStrictEqual(res.errors, []); res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0180-live-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length, res.posts.length);
  process.exit(res.status === "PASS" ? 0 : 1);
})();
