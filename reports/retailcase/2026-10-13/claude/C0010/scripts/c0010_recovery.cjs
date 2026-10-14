// C-0010: восстановление незавершённой команды. Чтение — реальный API (склад 9807, собственный расход C0010);
// POST подставляется только в сценарии «успех, но запись не удалилась» — реальной записи нет.
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const fs = require("fs");
const [OUT, CYCLE] = process.argv.slice(2);
const cycle = JSON.parse(fs.readFileSync(CYCLE, "utf8")).after;
const ORIGINAL = cycle.expenses[0].operation_id;
const PAGE = "http://127.0.0.1:5190/logistics-expenses.html";
async function open(b, init) {
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const p = await ctx.newPage(); const posts = [];
  p.on("request", (r) => { if (r.method() === "POST" && r.url().includes("/api/finance/")) posts.push(r.url()); });
  await p.goto(PAGE); await p.click("#loginFillAdmin"); await p.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit());
  await p.waitForFunction(() => !document.body.classList.contains("auth-pending"));
  if (init) { await p.evaluate(init.fn, init.arg); await p.reload(); await p.click("#loginFillAdmin").catch(() => {}); await p.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit()).catch(() => {}); await p.waitForFunction(() => !document.body.classList.contains("auth-pending")); }
  return { ctx, p, posts };
}
const keyFn = () => "logistics-expenses:" + wmsAdminAuth.state.apiBase.replace(/\/$/, "") + ":" + wmsAdminAuth.state.user.username;
(async () => {
  const b = await chromium.launch(); const res = {};
  // 1. Повреждённая запись, в которой виден ID регистрации: результат устанавливается точным поиском, затем запись закрывается.
  { const { ctx, p, posts } = await open(b, { fn: ([key, op]) => localStorage.setItem(new Function("return (" + key + ")")()(), '{"path":"/report","body":{"operation_id":"' + op + '","warehouse_id":9807,"amount":"12.34"'), arg: [keyFn.toString(), ORIGINAL] });
    res.damagedBefore = { banner: await p.textContent("#lxPending"), verifyVisible: await p.isVisible("#lxVerify"), restartVisible: await p.isVisible("#exRestart"), reportDisabled: await p.isDisabled("#exReport"), loadEnabled: await p.isEnabled("#exLoad") };
    await p.fill("#exWare", "9807"); await p.click("#exLoad"); await p.waitForFunction(() => /обновлены/.test(exMessage.textContent));
    await p.click("#lxVerify"); await p.waitForTimeout(800);
    res.damagedVerified = { message: await p.textContent("#exMessage"), banner: await p.textContent("#lxPending"), restart: await p.textContent("#exRestart") };
    await p.screenshot({ path: `${OUT}/c2_damaged_established.png` });
    await p.click("#exRestart"); await p.waitForTimeout(300);
    res.damagedClosed = { message: await p.textContent("#exMessage"), bannerHidden: await p.isHidden("#lxPending"), stored: await p.evaluate((k) => localStorage.getItem(new Function("return (" + k + ")")()()), keyFn.toString()), posts: posts.length };
    await ctx.close(); }
  // 2. Повреждённая запись с ID, которого на сервере нет: результат не установлен, удалить нельзя.
  { const { ctx, p } = await open(b, { fn: (key) => localStorage.setItem(new Function("return (" + key + ")")()(), '{"path":"/report","body":{"operation_id":"EXPENSE:00000000-0000-4000-8000-000000000000","warehouse_id":9807'), arg: keyFn.toString() });
    await p.fill("#exWare", "9807"); await p.click("#exLoad"); await p.waitForFunction(() => /обновлены/.test(exMessage.textContent));
    await p.click("#lxVerify"); await p.waitForTimeout(800);
    res.damagedUnknown = { message: await p.textContent("#exMessage"), restartVisible: await p.isVisible("#exRestart"), reportDisabled: await p.isDisabled("#exReport") };
    await ctx.close(); }
  // 3. Успех подтверждён, но удаление записи не удалось: новая команда не разрешается.
  { const { ctx, p, posts } = await open(b);
    await p.route(/logistics-expenses\/articles$/, (r) => r.request().method() === "POST" ? r.fulfill({ status: 200, headers: { "content-type": "application/json", "access-control-allow-origin": "*" }, body: JSON.stringify({ code: "DEV.C0010.MOCK", name: "x", scope: "TRIP", included_in_rate: false, active: true, version: 1 }) }) : r.continue());
    await p.fill("#exWare", "9807"); await p.click("#exLoad"); await p.waitForFunction(() => /обновлены/.test(exMessage.textContent));
    await p.evaluate(() => { Storage.prototype.removeItem = function () {}; });
    await p.fill("#exCode", "DEV.C0010.MOCK"); await p.fill("#exName", "mock only"); await p.click("#exArticle"); await p.waitForTimeout(1200);
    res.settled = { banner: await p.textContent("#lxPending"), restart: await p.textContent("#exRestart"), reportDisabled: await p.isDisabled("#exReport"), posts: posts.length };
    await p.click("#exRestart"); await p.waitForTimeout(300); res.settledCloseFails = { message: await p.textContent("#exMessage"), stillBlocked: await p.isDisabled("#exReport") };
    await p.screenshot({ path: `${OUT}/c2_settled_blocked.png` }); await ctx.close(); }
  fs.writeFileSync(`${OUT}/../c0010_recovery.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
