// C-0010 п.3: переходы из обзора сверки дня в существующие реестры с сохранением склада/даты/ID. Только чтение.
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const fs = require("fs");
const [OUT, CYCLE] = process.argv.slice(2);
const op = JSON.parse(fs.readFileSync(CYCLE, "utf8")).after.expenses[0].operation_id;
const BASE = "http://127.0.0.1:5190/";
async function login(p) { await p.click("#loginFillAdmin"); await p.locator("input[type=password]").evaluate((el) => el.closest("form").requestSubmit()); await p.waitForFunction(() => !document.body.classList.contains("auth-pending")); }
const links = (p) => p.$$eval("#dayOverview a.dr-link", (as) => as.map((a) => ({ text: a.textContent, href: a.getAttribute("href"), hint: a.parentElement.classList.contains("dr-link-wrap") ? a.parentElement.querySelector(".dr-link-hint").textContent : "" })));
(async () => {
  const b = await chromium.launch(); const res = {};
  for (const [label, vp] of [["desktop", { width: 1440, height: 1000 }], ["mobile", { width: 390, height: 844 }]]) {
    const ctx = await b.newContext({ viewport: vp }); const p = await ctx.newPage(); const errors = [];
    p.on("console", (m) => { if (m.type() === "error" && !/ws\/dispatch/.test(m.text())) errors.push(m.text()); });
    await p.goto(BASE + "day-reconciliation.html?warehouse_id=9807&day=2026-10-14"); await login(p);
    await p.waitForFunction(() => /сформирована|недоступна|Нет прав/.test(document.getElementById("drMessage").textContent), null, { timeout: 60000 });
    const out = { message: await p.textContent("#drMessage"), ware: await p.inputValue("#drWare"), day: await p.inputValue("#drDay"), url: p.url().replace(BASE, ""), links: await links(p), errors };
    if (label === "desktop") {
      await p.locator("#dayOverview").screenshot({ path: `${OUT}/d1_overview_desktop.png` });
      const iw = out.links.find((l) => l.href.startsWith("interwarehouse-groups.html"));
      const target = iw || out.links.find((l) => l.href.startsWith("logistics-expenses.html")) || out.links.find((l) => l.hint);
      if (target) {
        await p.click(`#dayOverview a.dr-link[href="${target.href}"]`); await p.waitForLoadState("load");
        await p.waitForFunction(() => !document.body.classList.contains("auth-pending"), null, { timeout: 30000 });
        out.followed = { href: target.href, landed: p.url().replace(BASE, "") };
        await p.goBack(); await p.waitForLoadState("load"); await p.waitForFunction(() => /сформирована/.test(document.getElementById("drMessage")?.textContent || ""), null, { timeout: 60000 });
        out.back = { url: p.url().replace(BASE, ""), ware: await p.inputValue("#drWare"), day: await p.inputValue("#drDay"), message: await p.textContent("#drMessage") };
      }
      out.builtExpenses = await p.evaluate(() => window.dayReconLinks.build({ kind: "registry", href: "logistics-expenses.html", label: "x" }, { warehouse_id: 9807, business_date: "2026-10-14" }));
      out.builtUnaware = await p.evaluate(() => window.dayReconLinks.build({ kind: "registry", href: "tare-ledger.html", label: "x" }, { warehouse_id: 9807, business_date: "2026-10-14" }));
      out.badDeepLink = await p.evaluate(() => { history.replaceState(null, "", "?warehouse_id=-5&day=2026-13-40"); return window.dayReconLinks.read(); });
    } else {
      const hinted = p.locator("#dayOverview .dr-link-wrap").first(); await hinted.scrollIntoViewIfNeeded(); await p.screenshot({ path: `${OUT}/d1_overview_mobile.png` });
      out.overflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    }
    res[label] = out; await ctx.close();
  }
  // Прямая ссылка на допрасходы: склад и точный расход (в том числе вне окна).
  { const ctx = await b.newContext({ viewport: { width: 1440, height: 1000 } }); const p = await ctx.newPage();
    await p.goto(BASE + "logistics-expenses.html?warehouse_id=9807&operation_id=" + encodeURIComponent(op)); await login(p);
    await p.waitForFunction(() => /найден/.test(document.getElementById("exMessage").textContent), null, { timeout: 40000 }).catch(() => {});
    res.expensesDeepLink = { ware: await p.inputValue("#exWare"), message: await p.textContent("#exMessage"), shown: await p.textContent("#lxShown"), query: await p.inputValue("#lxQuery") };
    await p.screenshot({ path: `${OUT}/d2_expenses_deeplink.png` }); await ctx.close(); }
  fs.writeFileSync(`${OUT}/../c0010_day_links.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
