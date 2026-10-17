// C0116: связь «старший смены ↔ ожидаемый состав» сохраняет выбранный склад (warehouse_id в адресе). Только чтение.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html";
(async () => {
  const b = await chromium.launch(); const res = { writes: [] };
  const p = await (await b.newContext({ viewport: { width: 1440, height: 1000 } })).newPage();
  p.on("request", r => { if (r.method() !== "GET" && r.url().includes(":8088/api/") && !r.url().endsWith("/shift-overview")) res.writes.push(r.method() + " " + r.url()); });
  const login = async () => { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); };
  await p.goto(BASE + "?workspace=shift&warehouse_id=20220394"); await login();
  await p.waitForSelector(".ops-kpi", { timeout: 30000 }); res.shiftWarehouse = await p.locator(".rg-window input[list]").first().inputValue();
  await p.getByRole("button", { name: "Ожидаемый состав" }).click(); await p.waitForTimeout(1500);
  if (await p.locator("input[type=password]").count()) await login();
  await p.waitForSelector(".ops-left", { timeout: 30000 }); await p.waitForTimeout(2000);
  res.consolidationUrl = new URL(p.url()).searchParams.get("warehouse_id"); res.consolidationWarehouse = await p.locator(".rg-window input[list]").first().inputValue();
  res.plans = await p.locator(".ops-left .ops-list li").count();
  await p.getByRole("button", { name: "Старший смены" }).click(); await p.waitForTimeout(1500);
  if (await p.locator("input[type=password]").count()) await login();
  await p.waitForSelector(".ops-kpi", { timeout: 30000 }); res.backWarehouse = await p.locator(".rg-window input[list]").first().inputValue();
  assert.equal(res.shiftWarehouse, "20220394"); assert.equal(res.consolidationWarehouse, "20220394"); assert.equal(res.backWarehouse, "20220394"); assert.deepEqual(res.writes, []);
  res.status = "PASS"; fs.writeFileSync(path.join(__dirname, "..", "shift_consolidation_nav_result.json"), JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
