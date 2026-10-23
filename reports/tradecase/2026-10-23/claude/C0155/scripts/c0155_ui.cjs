// C-0155 «Бумажные задания»: навигация из очереди и review печати бланка root (dev :3021) при 1440 и 390.
// ЖИВОЕ (только GET): вход, склады, scoped очередь склада 9104, root /paper (бланк, штрихкод, сверка версии; устаревшая версия = настоящий 409).
// FIXTURE: только 403 очереди. Записей нет: любой не-GET прерывается и фиксируется.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0155_BASE || "http://127.0.0.1:3021/", WH = "9104";
const res = { base: BASE, checks: [], liveWrites: [], errors: [], print: {}, timings: {} };
let fx = {};

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (m !== "GET") { res.liveWrites.push(m + " " + u); return r.abort(); }
  if (fx.queue403 && /\/api\/warehouse-tasks\?/.test(u)) return r.fulfill({ status: 403, json: { detail: "TASK_SCOPED_VIEW_REQUIRED" }, headers: { "access-control-allow-origin": "*" } });
  return r.continue();
}
const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };
const desk = p => p.locator("[aria-label='Бумажные задания']");

async function width(b, w, h) {
  fx = {};
  const ctx = await b.newContext({ viewport: { width: w, height: h } });
  await ctx.addInitScript(() => { window.print = () => { document.documentElement.dataset.printed = "1"; }; });  // no physical printer in the check
  const p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await ctx.route(u => u.href.includes(":8088/api/"), route);
  const t0 = Date.now();
  await p.goto(`${BASE}?page=workspace&workspace=paper&warehouse_id=${WH}`);
  const login = p.locator("input[type=password]");
  await Promise.race([login.waitFor({ timeout: 30000 }), desk(p).waitFor({ timeout: 30000 })]);
  if (await login.count()) { await p.fill("input[autocomplete=username]", "admin"); await login.fill(pass); await p.click("button[type=submit]"); }
  const first = desk(p).locator("li").first(); await first.waitFor({ timeout: 30000 });
  res.timings["queue_" + w] = Date.now() - t0;
  assert((await desk(p).innerText()).includes("Задание")); ok(w, "LIVE scoped queue of warehouse 9104: open tasks listed");
  const bad = await desk(p).locator("button").evaluateAll(bs => bs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every button has title and help id");

  await first.getByRole("button", { name: "Бланк" }).click();
  await first.getByRole("button", { name: "Бланк задания" }).click().catch(() => {});  // root panel starts closed inside the row
  await first.locator(".task-paper-fields").waitFor({ timeout: 30000 });
  const reference = (await first.locator(".task-paper code").textContent()).trim();
  assert(/^WTASK:\d+:[A-F0-9]{64}$/.test(reference)); ok(w, "LIVE root paper snapshot opened from the queue row");
  const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(over <= 1, "overflow " + over); ok(w, "no horizontal page scroll");
  await desk(p).screenshot({ path: path.join(SHOTS, `paper-queue-${w}.png`) });

  const [popup] = await Promise.all([ctx.waitForEvent("page"), first.getByRole("button", { name: "Печать / PDF" }).click()]);
  await popup.waitForLoadState(); await popup.locator("img").waitFor({ timeout: 15000 });
  await popup.waitForFunction(() => { const i = document.querySelector("img"); return i && i.complete && i.naturalWidth > 0; }, null, { timeout: 15000 });
  await popup.emulateMedia({ media: "print" });
  const probe = await popup.evaluate(() => { const i = document.querySelector("img").getBoundingClientRect(); const dds = [...document.querySelectorAll("dd")];
    return { printed: document.documentElement.dataset.printed === "1", img: { left: Math.round(i.left), right: Math.round(i.right), width: Math.round(i.width), height: Math.round(i.height) },
      viewport: innerWidth, scroll: document.documentElement.scrollWidth, fields: dds.length, clipped: dds.filter(d => d.scrollWidth > d.clientWidth + 1).length, title: document.title }; });
  res.print["popup_" + w] = probe;
  assert(probe.printed && probe.fields >= 8 && probe.clipped === 0 && probe.img.right <= probe.viewport + 1 && probe.scroll <= probe.viewport + 1, JSON.stringify(probe));
  ok(w, "print sheet: all fields readable, barcode inside the page, print dialog requested");
  await popup.screenshot({ path: path.join(SHOTS, `paper-print-${w}.png`), fullPage: true });
  if (w === 1440) { await popup.pdf({ path: path.join(OUT, "paper-print.pdf"), preferCSSPageSize: true }); ok(w, "PDF rendered with the sheet's own page size"); }
  await popup.close();

  const scan = desk(p).locator(".paper-scan");
  await scan.getByLabel("Штрихкод с бланка").fill(reference); await scan.getByRole("button", { name: "Сверить бланк" }).click();
  await scan.getByText("актуален").waitFor({ timeout: 30000 }); ok(w, "LIVE barcode reference of the printed sheet is current");
  const stale = reference.replace(/:[A-F0-9]{64}$/, ":" + "A".repeat(64));
  await scan.getByLabel("Штрихкод с бланка").fill(stale); await scan.getByRole("button", { name: "Сверить бланк" }).click();
  await scan.getByText("бланк устарел").waitFor({ timeout: 30000 }); assert(await scan.locator(".task-paper").count() === 0); ok(w, "LIVE changed version is refused (409) and no task is opened");
  await scan.getByLabel("Штрихкод с бланка").fill("not a code"); await scan.getByRole("button", { name: "Сверить бланк" }).click();
  await scan.getByText("Считайте штрихкод").waitFor(); ok(w, "garbage input is rejected locally");

  fx.queue403 = true; await desk(p).getByRole("button", { name: "Показать задания" }).click();
  await desk(p).getByText("Задания не прочитаны").waitFor(); assert(await desk(p).locator("li").count() === 0); ok(w, "403 clears the queue");
  await ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try { await width(b, 1440, 900); await width(b, 390, 844); assert.deepStrictEqual(res.errors, []); assert.deepStrictEqual(res.liveWrites, []); res.status = "PASS"; }
  catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0155-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length, "checks", JSON.stringify(res.timings));
  process.exit(res.status === "PASS" ? 0 : 1);
})();
