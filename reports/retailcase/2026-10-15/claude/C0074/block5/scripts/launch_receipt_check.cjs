// C-0094: read-only карточка квитанции запуска волны (NOT_VISIBLE ≠ откат), переход к факту волны. Только GET.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async () => {
  const b = await chromium.launch(); const res = { writes: [], errors: [] };
  const p = await (await b.newContext({ viewport: { width: 1000, height: 900 } })).newPage();
  p.on("request", r => { if (r.method() !== "GET" && r.url().includes("/api/")) res.writes.push(r.method() + " " + r.url()); });
  p.on("pageerror", e => res.errors.push(String(e)));
  await p.goto("http://127.0.0.1:3000/src/features/platform/workspaces/recovery/preview/index.html");
  await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  await p.waitForSelector("[data-help-id='launch-receipt.wave']", { timeout: 30000 });
  res.disabledBeforeInput = await p.getByRole("button", { name: "Прочитать квитанцию" }).getAttribute("aria-disabled");
  await p.locator("[data-help-id='launch-receipt.wave']").fill("561");
  await p.locator("[data-help-id='launch-receipt.operation']").fill("C0074-check-unknown-operation");
  await p.getByRole("button", { name: "Прочитать квитанцию" }).click(); await p.waitForTimeout(2500);
  res.card = (await p.locator(".ops-card").innerText()).replace(/\s+/g, " ").slice(0, 700);
  await p.screenshot({ path: `${OUT}/l1_launch_receipt.png` });
  const m = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage();
  await m.goto("http://127.0.0.1:3000/src/features/platform/workspaces/recovery/preview/index.html?wave_id=561&operation_id=x");
  await m.fill("input[autocomplete=username]", "admin"); await m.fill("input[type=password]", pass); await m.click("button[type=submit]"); await m.waitForTimeout(3000);
  res.mobileOverflow = await m.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  fs.writeFileSync(`${OUT}/../launch_receipt_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
