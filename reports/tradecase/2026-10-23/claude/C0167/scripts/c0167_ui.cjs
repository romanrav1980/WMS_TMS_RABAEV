// C-0167 «Смена машины» in the dispatcher trip card (dev :3021) at 1440 and 390.
// LIVE (GET only): login, deep link to trip 33664 and its card. FIXTURE: GET /api/transport/loading/33664/status in three states
// (not loaded / loaded / departed) and PATCH /api/admin/transport/tasks/33664 refused with the native code. Every other write is aborted.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0167_BASE || "http://127.0.0.1:3021/", TRIP = 33664;
const res = { base: BASE, trip: TRIP, checks: [], writes: [], errors: [], patches: [] };
const cors = { "access-control-allow-origin": "*" };
let fx = { state: "empty" };
const place = (id, status) => ({ load_operation_id: "LOAD." + id, root_uid: "PAL." + id, vehicle_number: "B22V1161", dock: "D1", status });
async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (u.includes(`/api/transport/loading/${TRIP}/status`) && m === "GET") {
    if (fx.state === "denied") return r.fulfill({ status: 403, headers: cors, json: { detail: { code: "LOADING_CURRENT_VIEW_ACTOR_REQUIRED" } } });
    const places = fx.state === "loaded" ? [place(1, "LOADED"), place(2, "LOADED")] : fx.state === "departed" ? [place(1, "DEPARTED")] : [];
    return r.fulfill({ status: 200, headers: cors, json: { trip: { id: TRIP, transport: "B22V1161", dock: "D1", condition: "Запланирован" }, physical_places: places } });
  }
  if (u.endsWith(`/api/admin/transport/tasks/${TRIP}`) && m === "PATCH") {
    res.patches.push(req.postDataJSON());
    return r.fulfill({ status: 409, headers: cors, json: { detail: { code: "TRANSPORT_EDIT_REJECTED", message: "ORA-20886: TRIP_CONFIRMED_UNLOADING_REQUIRED_BEFORE_REASSIGNMENT" } } });
  }
  if (m !== "GET" && !u.includes("/auth/")) { res.writes.push(m + " " + u); return r.abort(); }
  return r.continue();
}
const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };

async function width(b, w, h) {
  fx = { state: "empty" }; res.patches = [];
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await ctx.route(u => u.href.includes(":8088/api/"), route);
  await p.goto(`${BASE}?page=transport&task_id=${TRIP}`);
  const login = p.locator("input[type=password]"), edit = p.locator("button.dispatch-edit-btn"), title = p.getByText("Рейс #" + TRIP).first();
  await Promise.race([login.waitFor({ timeout: 30000 }), title.waitFor({ timeout: 30000 })]);
  if (await login.count()) { await p.fill("input[autocomplete=username]", "admin"); await login.fill(pass); await p.click("button[type=submit]"); }
  await title.waitFor({ timeout: 60000 }); ok(w, "LIVE dispatcher opens trip " + TRIP + " by deep link");
  await p.getByText("Заявки", { exact: true }).first().click();  // the editable trip card lives on the tasks tab
  await p.locator("input[type=date]").nth(1).fill("2026-10-22");
  await p.locator("tr", { hasText: "#" + TRIP }).first().click({ timeout: 30000 });
  await edit.waitFor({ timeout: 30000 });
  const baseline = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);  // the dispatcher page before the block
  await edit.click();
  const block = p.locator("[aria-label='Смена машины']");
  await block.getByText("машину можно сменить").waitFor({ timeout: 20000 });
  assert.match(await block.innerText(), /Текущая машина: B22V1161, рампа D1\.\s+Погружено мест: 0, выехало: 0/); ok(w, "FIXTURE not loaded: change allowed, assignments kept");
  fx.state = "loaded"; await block.getByRole("button", { name: "Обновить" }).click();
  await block.getByText("Сначала выгрузите погруженные места").waitFor();
  const t = await block.innerText();
  assert(/PAL\.1 — машина B22V1161, рампа D1/.test(t) && /скан новой машины/.test(t), t);
  const href = await block.getByRole("link", { name: "Открыть выгрузку рейса" }).getAttribute("href");
  assert(href.endsWith(`/transport-loading.html?trip_id=${TRIP}`), href); ok(w, "FIXTURE loaded: unload first, list of places, link to the existing unload screen");
  await p.locator(".dispatch-trip-ms").first().selectOption({ index: 1 }).catch(() => {});
  await p.getByRole("button", { name: /Сохранить/ }).first().click();
  await p.getByText(/Машину сменить нельзя: в рейсе есть погруженные/).first().waitFor({ timeout: 15000 });
  assert(res.patches.length === 1 && await edit.count() === 0, "the draft stays in edit mode after the refusal"); ok(w, "FIXTURE refusal in plain words; edit draft kept for retry (no [object Object])");
  fx.state = "departed"; await block.getByRole("button", { name: "Обновить" }).click();
  await block.getByText("Рейс выехал: смена машины недоступна").waitFor(); ok(w, "FIXTURE departed: change unavailable");
  const bad = await block.locator("button,a").evaluateAll(xs => xs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every block button/link has title and help id");
  const help = await ctx.request.get(new URL("/help/transport-vehicle-change.html", BASE).href);
  assert.equal(help.status(), 200); assert((await help.text()).includes("Смена машины у рейса")); ok(w, "local help answers 200");
  const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  const box = await block.evaluate(el => ({ right: el.getBoundingClientRect().right, width: el.scrollWidth, client: el.clientWidth }));
  res.overflow = res.overflow || {}; res.overflow[w] = { page_before_block: baseline, page_with_block: over, block: box };
  assert(over <= Math.max(1, baseline), "the block widens the page: " + over + " > " + baseline);
  assert(box.width <= box.client + 1, "the block itself overflows");
  ok(w, "the block adds no horizontal scroll (page baseline " + baseline + "px)");
  await block.screenshot({ path: path.join(SHOTS, `vehicle-change-${w}.png`) });
  fx.state = "denied"; await block.getByRole("button", { name: "Обновить" }).click();
  await block.getByText("Нет доступа к погрузке этого рейса.").waitFor();
  assert(!/Погружено мест/.test(await block.innerText())); ok(w, "FIXTURE 403 clears the places (no stale data)");
  await ctx.close();
}

(async () => {
  const b = await chromium.launch();
  try { await width(b, 1440, 1000); await width(b, 390, 844); assert.deepStrictEqual(res.errors, []); assert.deepStrictEqual(res.writes, []); res.status = "PASS"; }
  catch (e) { res.status = "FAIL"; res.error = String(e.stack || e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0167-ui.json"), JSON.stringify(res, null, 1));
  console.log(res.status, res.checks.length, "checks");
  process.exit(res.status === "PASS" ? 0 : 1);
})();
