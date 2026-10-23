// C-0167 «Смена машины» in the dispatcher trip card (dev :3021) at 1440 and 390.
// LIVE (GET only): login, deep link, the tasks tab and the real trip 33664 card and vehicle list.
// FIXTURE (labelled): GET /api/transport/loading/33664/status (not loaded / loaded / departed / 403); PATCH /api/admin/transport/tasks/33664
// outcomes (503, connection abort, 403, confirmed 409, 200); readback GET /api/admin/transport/tasks/33664 only while fx.readback is set.
// Every other write is aborted and recorded. Nothing reaches Oracle.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, ".."), SHOTS = path.join(OUT, "screenshots"); fs.mkdirSync(SHOTS, { recursive: true });
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const BASE = process.env.C0167_BASE || "http://127.0.0.1:3021/", TRIP = 33664, ORIGINAL = "B22V1161";
const res = { base: BASE, trip: TRIP, checks: [], writes: [], errors: [], overflow: {} };
const cors = { "access-control-allow-origin": "*" };
let fx;
const place = (id, status) => ({ load_operation_id: "LOAD." + id, root_uid: "PAL." + id, vehicle_number: ORIGINAL, dock: "D1", status });
async function route(r) {
  const req = r.request(), m = req.method(), u = req.url();
  if (m === "OPTIONS") return r.continue();
  if (u.includes(`/api/transport/loading/${TRIP}/status`) && m === "GET") {
    if (fx.state === "denied") return r.fulfill({ status: 403, headers: cors, json: { detail: { code: "LOADING_CURRENT_VIEW_ACTOR_REQUIRED" } } });
    const places = fx.state === "loaded" ? [place(1, "LOADED"), place(2, "LOADED")] : fx.state === "departed" ? [place(1, "DEPARTED")] : [];
    return r.fulfill({ status: 200, headers: cors, json: { trip: { id: TRIP, transport: ORIGINAL, dock: "D1", condition: "Запланирован" }, physical_places: places } });
  }
  if (u.endsWith(`/api/admin/transport/tasks/${TRIP}`) && m === "PATCH") {
    fx.patches.push(req.postData());
    const o = fx.patch.shift() || "200";
    if (o === "abort") return r.abort("connectionreset");
    if (o === "503") return r.fulfill({ status: 503, headers: cors, json: { detail: { code: "TRANSPORT_EDIT_UNCONFIRMED", message: "Повторите исходное изменение реквизитов" } } });
    if (o === "403") return r.fulfill({ status: 403, headers: cors, json: { detail: { code: "TRANSPORT_ACCESS_DENIED", message: "Недостаточно прав" } } });
    if (o === "409") return r.fulfill({ status: 409, headers: cors, json: { detail: { code: "TRANSPORT_EDIT_REJECTED", message: "ORA-20886: TRIP_CONFIRMED_UNLOADING_REQUIRED_BEFORE_REASSIGNMENT" } } });
    return r.fulfill({ status: 200, headers: cors, json: { ok: true } });
  }
  if (u.endsWith(`/api/admin/transport/tasks/${TRIP}`) && m === "GET" && fx.readback) {
    if (fx.readback === "403") return r.fulfill({ status: 403, headers: cors, json: { detail: "Недостаточно прав" } });
    const live = await (await r.fetch()).json();  // the real trip row with only the vehicle replaced
    return r.fulfill({ status: 200, headers: cors, json: { ...live, TRANSPORT: fx.readback } });
  }
  if (m !== "GET" && !u.includes("/auth/")) { res.writes.push(m + " " + u); return r.abort(); }
  return r.continue();
}
const ok = (w, name) => { res.checks.push({ width: w, name }); console.log("PASS", w, name); };

async function width(b, w, h) {
  fx = { state: "empty", patch: [], patches: [], readback: null };
  const ctx = await b.newContext({ viewport: { width: w, height: h } }), p = await ctx.newPage();
  p.on("pageerror", e => res.errors.push(w + ": " + e));
  await ctx.route(u => u.href.includes(":8088/api/"), route);
  const edit = p.locator("button.dispatch-edit-btn"), block = p.locator("[aria-label='Смена машины']"), pending = p.locator(".dispatch-vehicle-pending");
  async function openTrip() {
    await p.goto(`${BASE}?page=transport&task_id=${TRIP}`);
    const login = p.locator("input[type=password]"), title = p.getByText("Рейс #" + TRIP).first();
    await Promise.race([login.waitFor({ timeout: 30000 }), title.waitFor({ timeout: 30000 })]);
    if (await login.count()) { await p.fill("input[autocomplete=username]", "admin"); await login.fill(pass); await p.click("button[type=submit]"); }
    // Without rights the deep link itself is refused (403 shown in the header); the trip is then chosen in the tasks list.
    await title.or(p.getByText(`Рейс ${TRIP} не открыт`)).first().waitFor({ timeout: 60000 });
    await p.getByText("Заявки", { exact: true }).first().click();  // the editable trip card lives on the tasks tab
    await p.locator("input[type=date]").nth(1).fill("2026-10-22");
    await p.locator("tr", { hasText: "#" + TRIP }).first().click({ timeout: 30000 });
    await edit.or(p.locator("button.dispatch-save-btn")).first().waitFor({ timeout: 30000 });
  }
  async function editVehicle() {
    if (await edit.count()) await edit.click();
    const select = p.locator("select.dispatch-trip-ms").first();
    const values = await select.locator("option").evaluateAll(os => os.map(o => o.value).filter(Boolean));
    const target = values.find(v => v !== ORIGINAL); await select.selectOption(target); return target;
  }
  const save = () => p.locator("button.dispatch-save-btn").click();

  await openTrip(); ok(w, "LIVE dispatcher opens trip " + TRIP + " on the tasks tab");
  const baseline = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  await edit.click();
  await block.getByText("машину можно сменить").waitFor({ timeout: 20000 }); ok(w, "FIXTURE not loaded: change allowed, assignments kept");
  fx.state = "loaded"; await block.getByRole("button", { name: "Обновить" }).click();
  await block.getByText("Сначала выгрузите погруженные места").waitFor();
  assert((await block.getByRole("link", { name: "Открыть выгрузку рейса" }).getAttribute("href")).endsWith(`/transport-loading.html?trip_id=${TRIP}`));
  ok(w, "FIXTURE loaded: unload first, list of places, link to the existing unload screen");
  fx.state = "departed"; await block.getByRole("button", { name: "Обновить" }).click();
  await block.getByText("Рейс выехал: смена машины недоступна").waitFor(); ok(w, "FIXTURE departed: change unavailable");
  fx.state = "empty"; await block.getByRole("button", { name: "Обновить" }).click(); await block.getByText("машину можно сменить").waitFor();
  // 1. First confirmed 409: settled, plain words, nothing pending.
  const target = await editVehicle(); fx.patch = ["409"]; await save();
  await p.getByText(/Машину сменить нельзя: в рейсе есть погруженные/).first().waitFor({ timeout: 15000 });
  assert.equal(await pending.count(), 0, "a confirmed refusal leaves nothing pending"); ok(w, "FIXTURE first confirmed 409: plain refusal, no pending intent");
  // 2. 503: kept; reload; readback unchanged -> not saved; a new edit is refused; retry sends the same bytes; 200 settles.
  fx.patch = ["503"]; await save();
  await p.getByText(/Исход изменения рейса не подтверждён/).first().waitFor({ timeout: 15000 });
  const first = fx.patches.at(-1);
  fx.readback = ORIGINAL; await openTrip();
  await pending.getByText(/Изменение не сохранено: машина: сейчас «B22V1161»/).waitFor({ timeout: 20000 });
  ok(w, "FIXTURE 503 then reload: the original request survives and is read back as not saved");
  await editVehicle(); await save();
  await p.getByText(/У рейса есть неподтверждённое изменение/).first().waitFor();
  assert.equal(fx.patches.at(-1), first, "no new edited request replaced the unresolved original"); ok(w, "a new edit is refused while the original is unresolved");
  if (await p.locator("button.dispatch-cancel-edit-btn").count()) await p.locator("button.dispatch-cancel-edit-btn").click();
  // 2b. REVIEW2: the earlier attempt actually saved, then the trip froze; the retry gets 409 — that must not settle the intent.
  fx.patch = ["409"];
  await pending.getByRole("button", { name: "Повторить исходное изменение" }).click();
  await pending.getByText(/Сервер отклонил повтор, но прежняя попытка могла уже сохраниться/).waitFor({ timeout: 20000 });
  assert.equal(fx.patches.at(-1), first, "retry sends exactly the stored bytes");
  assert.equal(await pending.count(), 1, "a 409 after an unknown outcome keeps the original request"); ok(w, "after an unknown outcome a later 409 keeps the original request");
  fx.readback = target; await pending.getByRole("button", { name: "Проверить снова" }).click();
  await pending.getByText("Изменение рейса сохранено сервером.").waitFor({ timeout: 20000 });
  ok(w, "readback shows the earlier attempt saved: resolved without a further PATCH");
  // 2c. 503 again, reload, not saved, retry 200 settles.
  fx.readback = null; await openTrip(); await editVehicle(); fx.patch = ["503"]; await save();
  await p.getByText(/Исход изменения рейса не подтверждён/).first().waitFor({ timeout: 15000 });
  const second = fx.patches.at(-1); fx.readback = ORIGINAL; await openTrip();
  await pending.getByText(/Изменение не сохранено/).waitFor({ timeout: 20000 });
  fx.patch = ["200"]; fx.readback = target;
  await pending.getByRole("button", { name: "Повторить исходное изменение" }).click();
  await pending.getByText("Изменение рейса сохранено сервером.").waitFor({ timeout: 20000 });
  assert.equal(fx.patches.at(-1), second, "retry sends exactly the stored bytes"); ok(w, "retry sends the same bytes; success settles");
  // 3. Connection abort: kept; reload; readback already has the value -> settled without a second PATCH.
  fx.readback = null; await openTrip(); await editVehicle(); fx.patch = ["abort"]; const before = fx.patches.length; await save();
  await p.getByText(/Исход изменения рейса не подтверждён/).first().waitFor({ timeout: 15000 });
  fx.readback = target; await openTrip();
  await pending.getByText("Изменение рейса сохранено сервером.").waitFor({ timeout: 20000 });
  assert.equal(fx.patches.length, before + 1, "a saved change is not sent again"); ok(w, "connection abort then reload: readback shows it saved, no second PATCH");
  // 4. 403: kept; readback 403 keeps the intent, no retry/discard without a successful read.
  fx.readback = null; await openTrip(); await editVehicle(); fx.patch = ["403"]; await save();
  await p.getByText(/Нет прав на изменение рейса сейчас/).first().waitFor({ timeout: 15000 });
  fx.readback = "403"; await openTrip();
  await pending.getByText(/Нет доступа к рейсу: сверить нельзя/).waitFor({ timeout: 20000 });
  assert(await pending.getByRole("button", { name: "Повторить исходное изменение" }).isDisabled() && await pending.getByRole("button", { name: "Отказаться от изменения" }).isDisabled());
  ok(w, "403: intent kept, server data not shown, retry/discard disabled until a successful read");
  fx.readback = ORIGINAL; await pending.getByRole("button", { name: "Проверить снова" }).click();
  await pending.getByText(/Изменение не сохранено/).waitFor();
  await pending.getByRole("button", { name: "Отказаться от изменения" }).click();
  await p.waitForFunction(() => !document.querySelector(".dispatch-vehicle-pending")); ok(w, "after rights return and a read: discard clears the intent");
  fx.readback = null;
  // Hints, help, layout
  if (await edit.count()) await edit.click();
  await block.getByText("машину можно сменить").waitFor();
  const bad = await block.locator("button,a").evaluateAll(xs => xs.filter(x => !x.title || !x.dataset.helpId).map(x => x.textContent));
  assert.deepStrictEqual(bad, []); ok(w, "every block button/link has title and help id");
  const help = await ctx.request.get(new URL("/help/transport-vehicle-change.html", BASE).href);
  assert.equal(help.status(), 200); assert((await help.text()).includes("неподтверждённое")); ok(w, "local help answers 200 and covers the unknown outcome");
  const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  const box = await block.evaluate(el => ({ right: Math.round(el.getBoundingClientRect().right), scroll: el.scrollWidth, client: el.clientWidth }));
  const select = await p.locator("select.dispatch-trip-ms").first().evaluate(el => Math.round(el.getBoundingClientRect().right));
  res.overflow[w] = { page_before_block: baseline, page_with_block: over, block: box, vehicle_select_right: select };
  assert(over <= 1 && box.right <= w + 1 && box.scroll <= box.client + 1 && select <= w + 1, JSON.stringify(res.overflow[w]));
  ok(w, "no horizontal page scroll; block and vehicle select within the viewport");
  await p.screenshot({ path: path.join(SHOTS, `vehicle-change-${w}.png`), fullPage: false });
  fx.state = "denied"; await block.getByRole("button", { name: "Обновить" }).click();
  await block.getByText("Нет доступа к погрузке этого рейса.").waitFor();
  assert(!/Погружено мест/.test(await block.innerText())); ok(w, "FIXTURE 403 on loading clears the places (no stale data)");
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
