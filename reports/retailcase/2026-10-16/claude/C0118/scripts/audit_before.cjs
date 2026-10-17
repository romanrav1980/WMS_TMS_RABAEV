// C0118 аудит до правок: (1) сохраняется ли склад при переключении рабочих мест; (2) что перекрывает плавающая «? Справка» на 390 px;
// (3) какие семейства ресурсов видит общий Гант на живом складе. Только чтение.
const fs = require("fs"), path = require("path");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html";
const OUT = process.argv[2] || path.join(__dirname, "..");
(async () => {
  const b = await chromium.launch(); const res = { roles: {} };
  const p = await (await b.newContext({ viewport: { width: 1440, height: 1000 } })).newPage();
  await p.goto(BASE + "?workspace=shift&warehouse_id=6558233"); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  await p.waitForSelector(".ops-kpi", { timeout: 30000 });
  for (const role of ["Хранение и ричтраки", "Приёмка", "Консолидация", "Директор РЦ", "Диспетчер", "Старший смены"]) {
    await p.getByRole("tab", { name: role, exact: true }).click(); await p.waitForTimeout(1500);
    res.roles[role] = { url: new URL(p.url()).searchParams.get("warehouse_id"), inputs: await p.locator("input[list]").evaluateAll(i => i.map(x => x.value)) };
  }
  const m = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage();
  await m.goto(BASE + "?workspace=shift&warehouse_id=6558233"); await m.fill("input[autocomplete=username]", "admin"); await m.fill("input[type=password]", pass); await m.click("button[type=submit]");
  await m.waitForSelector(".ops-kpi", { timeout: 30000 }); await m.waitForTimeout(2000);
  res.launch = await m.evaluate(() => { const l = document.querySelector(".knowledge-launch")?.getBoundingClientRect(); return l ? { w: Math.round(l.width), h: Math.round(l.height) } : null; });
  res.covered = [];
  for (const y of [600, 1400, 2200]) {
    await m.evaluate(y => window.scrollTo(0, y), y); await m.waitForTimeout(200);
    res.covered.push(await m.evaluate(() => { const l = document.querySelector(".knowledge-launch"); const r = l.getBoundingClientRect(); l.style.visibility = "hidden";
      const under = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); l.style.visibility = "";
      const target = under?.closest("button,a,input,select,[role=button]"); return target ? (target.textContent || target.getAttribute("aria-label") || target.tagName).trim().slice(0, 40) : (under?.className?.toString().slice(0, 40) || null); }));
  }
  fs.writeFileSync(path.join(OUT, "audit_before.json"), JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
