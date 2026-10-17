// C-0093/C-0094: приёмка на календарном контракте поставок — warehouse_id и date_from/date_to/date_basis уходят серверу,
// backlog «без плановой даты» отдельно, окно > 31 дня не отправляется. Только чтение.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async () => {
  const b = await chromium.launch(); const res = { writes: [], supplyRequests: [], errors: [] };
  const p = await (await b.newContext({ viewport: { width: 1600, height: 1100 } })).newPage();
  p.on("request", r => { const u = r.url(); if (r.method() !== "GET" && u.includes("/api/")) res.writes.push(r.method() + " " + u);
    if (u.includes("/supply-orders?")) res.supplyRequests.push(decodeURIComponent(u.split("?")[1])); });
  p.on("pageerror", e => res.errors.push(String(e)));
  await p.goto("http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html?workspace=receiving");
  await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  await p.waitForSelector(".ops-kpi", { timeout: 30000 }); await p.waitForTimeout(3000);
  const snap = async () => ({ kpis: (await p.locator(".ops-kpi").allInnerTexts()).map(t => t.replace(/\s+/g, " ")),
    backlog: await p.locator("[data-help-id='receiving.backlog']").innerText().catch(() => "нет") });
  res.today = await snap();
  await p.locator("[data-help-id='receiving.filter.from']").fill("2026-10-01"); await p.waitForTimeout(2500);
  res.window = await snap();
  await p.locator("[data-help-id='receiving.filter.basis']").selectOption("ACCEPTED"); await p.waitForTimeout(2500);
  res.accepted = await snap();
  await p.locator(".rg-window input[list]").first().fill("31217707"); await p.waitForTimeout(2500);
  res.acceptedWarehouse = await snap();
  await p.screenshot({ path: `${OUT}/r4_receiving_calendar.png` });
  const before = res.supplyRequests.length;
  await p.locator("[data-help-id='receiving.filter.from']").fill("2026-08-01"); await p.waitForTimeout(1500);
  res.tooLong = { error: await p.locator(".ops-err").first().innerText().catch(() => "нет"), requestSent: res.supplyRequests.length > before };
  await p.getByRole("button", { name: /^День / }).click(); await p.waitForTimeout(2000);
  res.reset = await p.locator("[data-help-id='receiving.filter.from']").inputValue();
  fs.writeFileSync(`${OUT}/../receiving_calendar_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
