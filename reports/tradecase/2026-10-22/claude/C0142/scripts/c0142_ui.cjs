// C-0142 UI на собранном frontend (http://127.0.0.1:3000, актуальный API :8088).
// ЖИВОЕ: вход admin, реальные GET и read-only POST /api/picking/shift-overview; любые другие не-GET запросы обрываются и считаются ошибкой.
// FIXTURE (перехват, помечено в отчёте): 403/ошибки источников, событие на нескольких ресурсах, длинные названия, 403 Ганта после смены склада.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0142_BASE || "http://127.0.0.1:3000/";
const res = { base: BASE, checks: [], http: [], overview: [], writes: [], errors: [], fixtures: [], timings: {} };
let fx = {};   // активные fixture-режимы текущего шага
const cors = { "access-control-allow-origin": "*" };
const LONG = "Очень-длинное-название-ресурса-без-пробелов-для-проверки-обрезания-QA-".repeat(3);

function multiTimeline(u) {
  const q = new URL(u).searchParams, wh = +q.get("warehouse_id"), s = q.get("start_at"), f = q.get("finish_at");
  const at = h => new Date(Date.parse(s) + h * 3600e3).toISOString().replace(".000Z", "+00:00");
  const ev = (id, label, a, b) => ({ event_id: id, kind: "TRANSPORT_OPERATION", label, source: "RRL_TT_OPERATIONS", source_id: 1, trip_id: 900001, wave_id: null,
    plan_start_at: at(a), plan_finish_at: at(b), fact_start_at: null, fact_finish_at: null, time_status: "AWARE_PLAN", approval_status: "APPROVED" });
  return { warehouse_id: wh, start_at: s, finish_at: f, observed_at: at(1), warehouse_time_zone: null,
    resources: [{ resource_id: "DOCK:FX:1", kind: "DOCK", label: "FX-Ворота-1", warehouse_id: wh, source_state: "UNKNOWN", availability: "UNKNOWN" },
      { resource_id: "VEHICLE:FX", kind: "VEHICLE", label: LONG, warehouse_id: wh, source_state: null, availability: "UNKNOWN" },
      { resource_id: "RESOURCE:FX", kind: "CASE_PICKER", label: "FX-Комплектовщик", warehouse_id: wh, source_state: "AVAILABLE", availability: "UNKNOWN" }],
    events: [ev("FX:LOAD", "FIXTURE погрузка " + LONG, 2, 4)], unscheduled: [],
    assignments: ["DOCK:FX:1", "VEHICLE:FX", "RESOURCE:FX"].map(resource_id => ({ event_id: "FX:LOAD", resource_id })),
    sources: [{ source_id: "transport", status: "READY", permission: "transport_dispatch_view", limit: 2000, observed_at: at(1) }], overlap_candidates: [] };
}

async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (m !== "GET") {
    if (u.includes("/api/picking/shift-overview")) {
      res.overview.push(JSON.parse(req.postData() || "{}"));
      if (fx.overviewFail) { res.fixtures.push("shift-overview 503"); return r.fulfill({ status: 503, json: { detail: "fixture" }, headers: cors }); }
      return r.continue();
    }
    if (u.includes("/auth/")) return r.continue();
    res.writes.push(m + " " + u); return r.abort();
  }
  if (fx.caseDenied && u.includes("/api/case-pick/tasks")) { res.fixtures.push("case-pick/tasks 403"); return r.fulfill({ status: 403, json: { detail: { code: "ACCESS_DENIED" } }, headers: cors }); }
  if (fx.multi && u.includes("/api/resources/timeline")) { res.fixtures.push("timeline multi-resource"); return r.fulfill({ json: multiTimeline(u), headers: cors }); }
  if (fx.timelineDenied && u.includes("/api/resources/timeline") && u.includes("warehouse_id=" + fx.timelineDenied)) { res.fixtures.push("timeline 403"); return r.fulfill({ status: 403, json: { detail: { code: "ACCESS_DENIED" } }, headers: cors }); }
  return r.continue();
}

async function open(b, w, h, q) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  p.on("response", rr => { if (rr.url().includes(":8088/api/")) res.http.push(`${w} ${rr.request().method()} ${rr.status()} ${rr.url().replace(/^.*\/api\//, "/api/").slice(0, 120)}`); });
  await p.route(u => u.href.includes(":8088/api/"), route);
  const t0 = Date.now();
  await p.goto(BASE + "?page=workspace&workspace=shift&" + q);
  if (await p.locator("input[type=password]").count()) { await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]"); }
  return { p, ctx, t0 };
}
const noOverflow = p => p.evaluate(() => document.documentElement.scrollWidth <= innerWidth);
const ok = (w, name, extra = {}) => { res.checks.push({ width: w, name, ...extra }); console.log("PASS", w, name); };
const gantt = p => p.locator("section.rg[aria-label='Общий Гант ресурсов']");

async function liveWave613(b, w, h) {
  const { p, ctx, t0 } = await open(b, w, h, "warehouse_id=220793322");
  const item = p.locator("g[role=button][aria-label='Волна NB22.B.220793322']");
  await item.waitFor({ timeout: 30000 });
  await p.waitForFunction(() => [...document.querySelectorAll("g[role=button] title")].some(t => /Собрано: контроль, погрузка/.test(t.textContent)), null, { timeout: 30000 });
  res.timings["scene613_" + w] = Date.now() - t0;
  const title = await item.locator("title").textContent(); assert(/Собрано: контроль, погрузка/.test(title), title);
  ok(w, "LIVE wave 613 (CASE1169 CONTROLLED) stands on actual stage 'Собрано', not static CLEAR", { ms: res.timings["scene613_" + w] });
  await item.focus(); await p.keyboard.press("Enter");                               // клавиатура: Tab-фокус + Enter
  const card = p.locator("section[aria-label='Волна NB22.B.220793322']"); await card.waitFor({ timeout: 30000 });
  await p.waitForFunction(() => /собрано, ждёт контроля или погрузки/.test(document.querySelector("section[aria-label='Волна NB22.B.220793322']")?.textContent || ""), null, { timeout: 30000 });
  res.timings["card613_" + w] = Date.now() - t0;
  assert.equal(new URL(p.url()).searchParams.get("wave_id"), "613");
  ok(w, "LIVE keyboard Enter opens wave card with actual picking stage; wave_id in URL", { ms: res.timings["card613_" + w] });
  await card.getByRole("button", { name: "Ресурсы волны в Ганте" }).click();
  await gantt(p).locator("[data-help-id='resource-gantt.wave.filter']").waitFor({ timeout: 30000 });
  assert(await card.isVisible(), "wave card stays open (return context)");
  ok(w, "LIVE wave → Gantt exact wave filter, wave card kept");
  await gantt(p).getByRole("button", { name: "Снять фильтр волны" }).click();
  assert.equal(await gantt(p).locator("[data-help-id='resource-gantt.wave.filter']").count(), 0);
  // Риски: живые источники прочитаны — блока «проверено не полностью» нет.
  await card.getByRole("button", { name: "Закрыть карточку" }).click();
  await p.locator("button[data-help-id='shift.process.risks']").click();
  const panel = p.locator("section.ops-card[aria-label='Риски запуска']"); await panel.waitFor();
  const text = await panel.innerText(); res.liveRisks = text.slice(0, 400);
  assert(!/Проверено не полностью/.test(text) && !/Existing usable own target coverage/.test(await panel.innerText()), text);
  ok(w, "LIVE risks panel: all sources read, no gap block; cancelled replenishment 1673 not shown as waiting");
  assert(await noOverflow(p), "page horizontal overflow");
  await p.screenshot({ path: path.join(SHOTS, `live-shift-613-${w}.png`), fullPage: w === 390 });
  await ctx.close();
}

async function liveDone604(b, w, h) {
  const { p, ctx, t0 } = await open(b, w, h, "warehouse_id=220639789&wave_id=604");
  const card = p.locator("section[aria-label='Волна FP21.220639789']"); await card.waitFor({ timeout: 30000 });
  const t = await card.innerText(); assert(/Завершена/.test(t) && !/Риски запуска/.test(t), t);
  res.timings["done604_" + w] = Date.now() - t0;
  ok(w, "LIVE completed wave 604 opens from header outside active lists; archive card without launch risks", { ms: res.timings["done604_" + w] });
  await ctx.close();
}

async function liveUntimed9807(b, w, h) {
  const { p, ctx } = await open(b, w, h, "warehouse_id=9807");
  const g = p.locator("section[aria-label='Общий Гант ресурсов'] .rg-planner");
  await g.locator("input[type=datetime-local]").waitFor({ timeout: 30000 });
  await g.locator("input[type=datetime-local]").fill("2026-10-15T00:00");
  await g.locator("input[type=number]").fill("168");
  const row = gantt(p).locator("button.rg-label", { hasText: "QC241ede877f6d1" }); await row.waitFor({ timeout: 30000 });
  const label = await row.innerText(); assert(/без времени 12/.test(label), label);
  await row.click();
  const rc = p.locator("section.ops-card[aria-label='Ресурс QC241ede877f6d1']"); await rc.waitFor();
  const rt = await rc.innerText(); assert(/Назначены без времени\s*12/.test(rt) && /у назначенных работ нет времени/.test(rt) && /Неизвестно/.test(rt), rt);
  ok(w, "LIVE 9807 vehicle with 12 untimed transport operations: row marked, card lists them, state Unknown (not free)");
  await rc.getByRole("button", { name: "Работа" }).first().click();
  const ec = p.locator("section.ops-card[aria-label^='Работа DOCK_ASSIGN']"); await ec.waitFor();
  const et = await ec.innerText(); assert(/времени на шкале нет/.test(et) && /источник изменился после утверждения/.test(et) && !/Ресурс не назначен/.test(et) && !/TIME_UNRESOLVED/.test(et), et);
  ok(w, "LIVE event card keeps vehicle as resource, plain time/approval text, no 'no resource'");
  await ec.getByRole("button", { name: "Ресурс" }).first().click(); await rc.waitFor();
  ok(w, "LIVE event → resource return path");
  assert(await noOverflow(p));
  await p.screenshot({ path: path.join(SHOTS, `live-untimed-9807-${w}.png`), fullPage: w === 390 });
  await ctx.close();
}

async function fixtureGaps(b, w, h) {
  fx = { caseDenied: true, overviewFail: true };
  const { p, ctx } = await open(b, w, h, "warehouse_id=220793322");
  await p.locator("button[data-help-id='shift.process.risks']").click();
  const panel = p.locator("section.ops-card[aria-label='Риски запуска']"); await panel.waitFor({ timeout: 30000 });
  await p.waitForFunction(() => /подробно не проверено волн/.test(document.querySelector("section.ops-card[aria-label='Риски запуска']")?.textContent || ""), null, { timeout: 30000 });
  const t = await panel.innerText(); assert(/Проверено не полностью/.test(t) && /сборка: Нет права/.test(t) && !/Подтверждённых рисков по прочитанным источникам нет/.test(t), t);
  const st = await p.locator("g[role=button][aria-label='Волна NB22.B.220793322'] title").textContent(); assert(/Детали не прочитаны/.test(st), st);
  ok(w, "FIXTURE 403 case tasks + 503 overview: risks panel lists gaps, never 'no risks'; wave stays 'Детали не прочитаны'");
  await p.screenshot({ path: path.join(SHOTS, `fixture-gaps-${w}.png`) });
  fx = {}; await ctx.close();
}

async function fixtureMultiAndSwitch(b, w, h) {
  fx = { multi: true };
  const { p, ctx } = await open(b, w, h, "warehouse_id=220793322&wave_id=613");
  await p.locator("section[aria-label='Волна NB22.B.220793322']").waitFor({ timeout: 30000 });
  const bar = gantt(p).locator("button.rg-bar", { hasText: "FIXTURE погрузка" }); await bar.first().waitFor({ timeout: 30000 });
  assert.equal(await bar.count(), 3);
  await bar.first().click();
  const ec = p.locator("section.ops-card[aria-label^='Работа FIXTURE погрузка']"); await ec.waitFor();
  const et = await ec.innerText(); assert(/Ресурсы работы\s*3/.test(et) && /ворота/.test(et) && /машина/.test(et) && /исполнитель/.test(et), et);
  const sum = await gantt(p).locator(".rg-summary").innerText(); assert(/работ 1 \(по event_id\)/.test(sum) && /назначений 3/.test(sum), sum);
  ok(w, "FIXTURE one event on dock+vehicle+picker: 3 bars, one card with 3 roles, counted once");
  assert(await noOverflow(p), "long names overflow page");
  await p.screenshot({ path: path.join(SHOTS, `fixture-multi-long-${w}.png`), fullPage: w === 390 });
  ok(w, "FIXTURE long resource/work names: no page horizontal overflow");
  // Смена склада: карточка волны и выбор очищаются; Гант другого склада 403 — старый Гант не показывается.
  fx = { timelineDenied: "219023232" };
  const input = p.locator("input[data-help-id='resource-gantt.warehouse']").first();
  await input.fill("219023232");
  await p.waitForFunction(() => !document.querySelector("section[aria-label='Волна NB22.B.220793322']"), null, { timeout: 30000 });
  await p.locator("section[aria-label='Общий Гант ресурсов'] .ops-err", { hasText: "Нет права" }).waitFor({ timeout: 30000 });
  assert.equal(await gantt(p).count(), 0); assert.equal(new URL(p.url()).searchParams.get("wave_id"), null);
  ok(w, "FIXTURE warehouse switch clears wave card/URL wave; Gantt 403 shows no previous warehouse data");
  fx = {}; await ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try {
    for (const [w, h] of [[1440, 1000], [390, 844]]) {
      await liveWave613(b, w, h); await liveDone604(b, w, h); await liveUntimed9807(b, w, h); await fixtureGaps(b, w, h); await fixtureMultiAndSwitch(b, w, h);
    }
    assert.deepEqual(res.errors, []); assert.deepEqual(res.writes, []);
    res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  res.asset = (await (await fetch(BASE)).text()).match(/assets\/index-[^"]+\.js/)?.[0];
  res.counts = { checks: res.checks.length, http: res.http.length, overviewPosts: res.overview.length, writes: res.writes.length, jsErrors: res.errors.length };
  fs.writeFileSync(path.join(OUT, "c0142-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, JSON.stringify(res.counts), JSON.stringify(res.timings));
  await b.close(); process.exit(res.status === "PASS" ? 0 : 1);
})();
