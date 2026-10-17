// C0124: путь старшего смены «склад → волна (готовность/риски) → задание сборки → Гант (карточка работы/ресурс) → назад к волне»
// на desktop и 390. Живой API, только чтение (вход admin). Изменяющих запросов нет. Пароль не печатается.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "..", "screenshots");
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html";
const WH = process.env.C0124_WH || "9278842";
const res = { writes: [], errors: [], runs: {} };

async function run(b, w, h) {
  const p = await (await b.newContext({ viewport: { width: w, height: h } })).newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  p.on("request", r => { if (r.method() !== "GET" && r.url().includes(":8088/api/") && !r.url().endsWith("/shift-overview")) res.writes.push(r.method() + " " + r.url()); });
  await p.goto(BASE + "?workspace=shift&warehouse_id=" + WH);
  await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  await p.waitForSelector(".ops-kpi", { timeout: 30000 });
  await p.waitForFunction(() => /[1-9]\d* из [1-9]\d* видимых волн/.test(document.querySelector(".ops-left .ops-note")?.textContent || ""), null, { timeout: 30000 });
  const r = {};
  // Волна: выбираем волну, у которой есть задания сборки.
  const waves = await p.locator("g[role=button][aria-label^='Волна']").evaluateAll(n => n.map(x => x.getAttribute("aria-label")));
  r.waves = waves.length;
  for (const label of waves) {
    await p.locator(`g[role=button][aria-label="${label}"]`).first().click();
    await p.waitForSelector(".ops-right .ops-card h3");
    if (await p.locator(".ops-right .ops-card").getByRole("button", { name: "В Ганте", exact: true }).count()) { r.wave = label; break; }
  }
  assert(r.wave, "нет волны с заданиями сборки");
  const card = p.locator(".ops-right .ops-card").first();
  r.waveTitle = (await card.locator("h3").first().innerText()).slice(0, 80);
  r.readiness = await card.locator("dl").first().innerText().then(t => t.slice(0, 200));
  r.risksHeading = await card.locator("h3", { hasText: "Риски запуска" }).innerText();
  // Задание → Гант.
  await card.getByRole("button", { name: "В Ганте", exact: true }).first().click(); await p.waitForTimeout(2000);
  r.ganttVisible = await p.locator(".rg-planner").isVisible();
  r.cards = await p.locator("section[aria-label='Общий Гант ресурсов'] .ops-card").evaluateAll(n => n.map(x => (x.getAttribute("aria-label") || "") + " | " + (x.querySelector("h3")?.textContent || "").slice(0, 80)));
  r.workCard = await p.locator("section[aria-label='Общий Гант ресурсов'] [aria-label^='Работа']").first().innerText().catch(() => "");
  r.ganttInView = await p.locator(".rg-planner").evaluate(e => { const b = e.getBoundingClientRect(); return b.top < innerHeight && b.bottom > 0; });
  // Назад к волне из карточки работы (поле «Волна»).
  const back = p.locator("[data-help-id='resource-gantt.open.wave'], .rg-planner dd button").first();
  r.backButton = await back.count();
  if (r.backButton) { await back.click(); await p.waitForTimeout(1200);
    r.backToWave = await p.locator(".ops-right .ops-card h3").first().innerText().then(t => t.slice(0, 80)); }
  r.overflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  await p.screenshot({ path: path.join(OUT, `p1_path_${w}.png`) });
  res.runs[w] = r; await p.context().close();
}

(async () => {
  const b = await chromium.launch();
  await run(b, 1440, 1000); await run(b, 390, 844);
  for (const r of Object.values(res.runs)) { assert(r.ganttVisible && r.backButton && r.backToWave === r.waveTitle && r.overflow <= 0, JSON.stringify(r)); }
  assert.deepEqual(res.writes, []); assert.deepEqual(res.errors, []); res.status = "PASS";
  fs.writeFileSync(path.join(__dirname, "..", "path_check.json"), JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e.message); console.error(JSON.stringify(res, null, 1)); process.exit(1); });
