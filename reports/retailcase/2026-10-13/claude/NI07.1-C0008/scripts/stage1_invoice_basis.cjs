// C-0008 этап 1: прямое основание допрасхода в карточке счёта. Только чтение.
// Строки расходов — реальный ответ GET /api/finance/expense-allocation/billing-orders/0 стенда (рейсы без счёта),
// подставленные в пустой счёт БТ-0528 только в этом тесте, потому что ни один реальный счёт стенда расходов не содержит.
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const fs = require("fs");
const [OUT, REAL] = process.argv.slice(2);
const real = JSON.parse(fs.readFileSync(REAL, "utf8"));
const CORS = { "access-control-allow-origin": "http://127.0.0.1:5183", "access-control-allow-credentials": "true", "access-control-allow-headers": "authorization,content-type", "access-control-allow-methods": "GET,POST,OPTIONS" };
const OLD_KEYS = ["ware_id","expense_date","reporter","article_code","expected_confirmed_total","confirmed_total","logist_operation_id","logist_outcome","logist_actor","logist_decision_reference","finance_operation_id","finance_actor","finance_decision_reference"];
const strip = (rows) => rows.map((r) => Object.fromEntries(Object.entries(r).filter(([k]) => !OLD_KEYS.includes(k))));
async function run(b, label, rows, viewport) {
  const ctx = await b.newContext({ viewport, serviceWorkers: "block" }); const p = await ctx.newPage(); const regReads = [];
  p.on("request", (r) => { if (/logistics-expenses\/warehouses\//.test(r.url())) regReads.push(r.url()); });
  await p.route(/expense-allocation\/billing-orders\/528$/, (route) => route.request().method() === "OPTIONS" ? route.fulfill({ status: 204, headers: CORS }) : route.fulfill({ status: 200, headers: { ...CORS, "content-type": "application/json" }, body: JSON.stringify(rows) }));
  await p.goto("http://127.0.0.1:5183/?page=transport");
  await p.locator(".dispatch-tab, button", { hasText: "Биллинг" }).first().click(); await p.waitForTimeout(1200);
  const dates = p.locator("input[type=date]"); if (await dates.count() >= 2) { await dates.nth(0).fill("2026-01-01"); await dates.nth(1).fill("2026-12-31"); }
  const refresh = p.locator("button", { hasText: "⟳" }).first(); if (await refresh.count()) await refresh.click();
  await p.waitForSelector("text=БТ-0528", { timeout: 30000 }); await p.getByText("БТ-0528", { exact: true }).first().click();
  await p.waitForSelector("#bcExpensesTitle"); await p.waitForSelector("tr:has-text('EX.CORRECT:')");
  const out = { label };
  await p.locator("tr", { hasText: "EX.CORRECT:47517f0309" }).getByRole("button", { name: "Основание" }).click(); await p.waitForSelector(".bc-basis dl");
  await p.waitForTimeout(400); out.correction = await p.locator(".bc-basis").innerText();
  await p.locator(".bc-basis").screenshot({ path: `${OUT}/s1_${label}_correction.png` });
  const jump = p.getByRole("button", { name: /Открыть исходный расход EX.PRECISION/ });
  if (await jump.count()) { await jump.click(); await p.waitForTimeout(300); out.original = await p.locator(".bc-basis").innerText(); }
  await p.locator("tr", { hasText: "CORR601.0" }).getByRole("button", { name: "Основание" }).click(); await p.waitForTimeout(500);
  out.normative = await p.locator(".bc-basis").innerText();
  await p.locator(".bc-root").screenshot({ path: `${OUT}/s1_${label}_invoice.png` });
  out.expensesBlock = (await p.locator("section[aria-labelledby=bcExpensesTitle]").innerText()).slice(0, 1500);
  out.registryReads = regReads.length; await ctx.close(); return out;
}
(async () => {
  const b = await chromium.launch(); const res = [];
  res.push(await run(b, "direct_desktop", real, { width: 1440, height: 900 }));
  res.push(await run(b, "direct_mobile", real, { width: 390, height: 844 }));
  res.push(await run(b, "old_server", strip(real), { width: 1440, height: 900 }));
  fs.writeFileSync(`${OUT}/../stage1_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res.map((r) => ({ label: r.label, registryReads: r.registryReads, correction: r.correction.slice(0, 600), normative: r.normative.slice(0, 500) })), null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
