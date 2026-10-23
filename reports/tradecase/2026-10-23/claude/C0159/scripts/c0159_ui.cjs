// C-0159 риски хода волны и сроков на рабочем месте старшего смены (dev :3021) при 1440 и 390.
// ЖИВОЕ: вход, все GET и read-only POST /api/picking/shift-overview складов 6667491 (волна 395: отбор разрешён, 2 задания NEW без
// исполнителя, утверждённый план времени с прошедшим окончанием) и 20220394 (WAIT_CONTROL в волнах 571/573).
// FIXTURE (помечено): 403 сессий ресурсов, 403 заданий сборки, задержанный ответ заданий старого склада. Записей нет.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0159_BASE || "http://127.0.0.1:3021/";
const res = { base: BASE, checks: [], writes: [], errors: [], fixtures: [], overview: 0, live: {}, timings: {} };
const cors = { "access-control-allow-origin": "*" };
let fx = {};

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (m !== "GET") {
    if (u.includes("/api/picking/shift-overview")) { res.overview++; return r.continue(); }
    if (u.includes("/auth/")) return r.continue();  // sign-in, not a warehouse command
    res.writes.push(m + " " + u); return r.abort();
  }
  if (fx.sessions403 && u.includes("/api/resources/sessions")) { res.fixtures.push("sessions 403"); return r.fulfill({ status: 403, json: { detail: { code: "ACCESS_DENIED" } }, headers: cors }); }
  if (fx.case403 && u.includes("/api/case-pick/tasks")) { res.fixtures.push("case tasks 403"); return r.fulfill({ status: 403, json: { detail: { code: "ACCESS_DENIED" } }, headers: cors }); }
  if (fx.slowWare && u.includes("/api/case-pick/tasks") && u.includes("ware_id=" + fx.slowWare)) { res.fixtures.push("case tasks delayed " + fx.slowWare); await new Promise(ok => setTimeout(ok, 2500)); }
  return r.continue();
}
const ok = (w, name, extra = {}) => { res.checks.push({ width: w, name, ...extra }); console.log("PASS", w, name); };
const risksPanel = p => p.locator("section.ops-card[aria-label='Риски запуска']");

async function open(b, w, h, ware) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await p.route(u => u.href.includes(":8088/api/"), route);
  const t0 = Date.now();
  await p.goto(`${BASE}?page=workspace&workspace=shift&warehouse_id=${ware}`);
  const login = p.locator("input[type=password]"), proc = p.locator("button[data-help-id='shift.process.risks']");
  await Promise.race([login.waitFor({ timeout: 30000 }), proc.waitFor({ timeout: 30000 })]);
  if (await login.count()) { await p.fill("input[autocomplete=username]", "admin"); await login.fill(pass); await p.click("button[type=submit]"); }
  await proc.waitFor({ timeout: 30000 });
  return { p, ctx, t0 };
}
async function risks(p, pattern) {
  await p.locator("button[data-help-id='shift.process.risks']").click();
  await risksPanel(p).waitFor({ timeout: 30000 });
  await p.waitForFunction(re => new RegExp(re).test(document.querySelector("section.ops-card[aria-label='Риски запуска']")?.textContent || ""), pattern, { timeout: 45000 });
  return risksPanel(p).innerText();
}

async function width(b, w, h) {
  fx = {};
  // LIVE 6667491: unassigned tasks + deadline of the approved plan, on real reads.
  let { p, ctx, t0 } = await open(b, w, h, 6667491);
  let text = await risks(p, "Задания без исполнителя");
  res.timings["risks_6667491_" + w] = Date.now() - t0; res.live["6667491_" + w] = text.slice(0, 1500);
  assert(/Задания без исполнителя: (не меньше )?\d+/.test(text) && /волна 395/.test(text), text);
  assert(/открытых сессий комплектовщиков|сессии комплектовщиков не проверены полностью/.test(text), text);
  ok(w, "LIVE 6667491: wave 395 unassigned tasks with the session fact (not a 'free resource')");
  const deadline = /Утверждённое окончание волны прошло \d+ мин назад/.test(text), approvedChanged = !deadline && /Время волны не утверждено/.test(text);
  res.live["deadline_" + w] = deadline ? "APPROVED finish passed" : approvedChanged ? "time-context not APPROVED for 395" : "none";
  assert(deadline, "expected the approved-plan deadline risk for wave 395: " + text);
  ok(w, "LIVE 6667491: approved plan of wave 395 finished in the past → deadline blocker by the server clock");
  const bad = await p.locator("section.ops-card[aria-label='Риски запуска'] button, aside[aria-label='Процессы старшего смены'] button").evaluateAll(bs => bs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every risk/process button has title and help id");
  const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth); assert(over <= 1, "overflow " + over); ok(w, "no horizontal page scroll");
  await risksPanel(p).screenshot({ path: path.join(SHOTS, `shift-risks-6667491-${w}.png`) });
  // The risk's wave link opens the real selected-wave card with the same login.
  await risksPanel(p).locator("li", { hasText: "Задания без исполнителя" }).getByRole("button", { name: "Волна" }).click();
  await p.waitForFunction(() => /wave_id=395/.test(location.search), null, { timeout: 15000 });
  assert(await p.locator("input[type=password]").count() === 0); ok(w, "risk 'Волна' opens wave 395 card in place (wave_id in the URL), login kept");
  await ctx.close();

  // LIVE 20220394: control.
  ({ p, ctx } = await open(b, w, h, 20220394));
  text = await risks(p, "Ждут контроля");
  res.live["20220394_" + w] = text.slice(0, 1500);
  assert(/Ждут контроля: (не меньше )?\d+ коробов/.test(text) && /волна 57[13]/.test(text), text); ok(w, "LIVE 20220394: waves 571/573 boxes waiting for control");
  await ctx.close();

  // FIXTURE: sessions revoked → gap listed and impact says 'not checked', never 'no sessions'.
  fx.sessions403 = true; ({ p, ctx } = await open(b, w, h, 6667491));
  text = await risks(p, "Задания без исполнителя");
  assert(/сессии ресурсов: /.test(text) && /сессии комплектовщиков не проверены полностью/.test(text) && !/открытых сессий комплектовщиков на складе нет/.test(text), text);
  ok(w, "FIXTURE 403 sessions: verification gap, unassigned impact 'not fully checked'"); fx.sessions403 = false; await ctx.close();

  // FIXTURE: CASE tasks revoked → no control/unassigned risks, gap instead of 'no risks'.
  fx.case403 = true; ({ p, ctx } = await open(b, w, h, 20220394));
  text = await risks(p, "сборка: ");
  assert(!/Ждут контроля/.test(text) && !/Задания без исполнителя/.test(text) && /Проверено не полностью/.test(text), text);
  ok(w, "FIXTURE 403 case tasks: control/assignment risks cleared, gap shown"); fx.case403 = false; await ctx.close();

  // FIXTURE late answer: tasks of 6667491 delayed, warehouse switched to 20220394 in the picker of the same page → no wave-395 risk appears.
  fx.slowWare = "6667491"; ({ p, ctx } = await open(b, w, h, 6667491));
  await p.locator("input[list='rg-wh-waves']").fill("20220394");  // in-app warehouse switch, same login
  text = await risks(p, "Ждут контроля"); await p.waitForTimeout(3000);
  text = await risksPanel(p).innerText();
  assert(!/волна 395/.test(text), text); ok(w, "FIXTURE delayed tasks of the previous warehouse do not leak into the new warehouse's risks");
  fx.slowWare = null; await ctx.close();

  // Static help link of the article.
  ({ p, ctx } = await open(b, w, h, 6667491));
  const href = await p.locator("a[data-help-id='shift.navigation.help']").getAttribute("href");
  const help = await ctx.request.get(href); assert.equal(help.status(), 200, href); await ctx.close();
  ok(w, "static help link of the shift bar answers 200: " + href);
}

(async () => {
  const b = await chromium.launch();
  try { await width(b, 1440, 1000); await width(b, 390, 844); assert.deepStrictEqual(res.errors, []); assert.deepStrictEqual(res.writes, []); res.status = "PASS"; }
  catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0159-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length, "checks", JSON.stringify(res.timings));
  process.exit(res.status === "PASS" ? 0 : 1);
})();
