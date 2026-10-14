// C-0032: восстановление утверждения времени рейса после перезагрузки. GET плана — реальный;
// POST /time-approvals перехватывается (mocked evidence): реальный рейс не утверждается.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const KEY = 'nicora.trip.time.pending:["http://127.0.0.1:8088","admin"]';
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 1440, height: 950 }, serviceWorkers: "block" });
  const p = await ctx.newPage(); const posts = []; let mode = "abort"; const res = {};
  await p.route("**/api/transport/preflight/time-approvals", async (route) => {
    const body = JSON.parse(route.request().postData()); posts.push(body);
    if (mode === "abort") return route.abort("failed");
    return route.fulfill({ status: 200, headers: { "access-control-allow-origin": "*", "content-type": "application/json" }, body: JSON.stringify({ operation_id: body.operation_id, trip_id: body.trip_id, actor: "admin", status: "APPROVED" }) });
  });
  // Только для открытия карточки: операции рейса стоят в 00:00–01:52 (вне видимой шкалы 06–22), поэтому ответ диаграммы
  // подставляется со сдвигом на 08:00 и вторым рейсом 33571 (mock отображения). План рейса /time-context читается реально.
  await p.route("**/api/admin/transport/vehicles/gantt**", async (route) => {
    const real = await (await route.fetch()).json();
    const shift = (t) => t && t.replace(/ 0(\d):/, (m, h) => " " + String(8 + Number(h)).padStart(2, "0") + ":");
    const rows = real.map((v) => ({ ...v, operations: v.operations.map((o) => ({ ...o, plan_start: shift(o.plan_start), plan_end: shift(o.plan_end) })) }));
    if (rows[0]) rows.push({ ...rows[0], vehicle_id: (rows[0].vehicle_id || 0) + 1, vehicle_num: "MOCK-33571", operations: rows[0].operations.slice(0, 3).map((o, i) => ({ ...o, op_id: (o.op_id || 0) + 100000 + i, tt_id: 33571, plan_start: shift(o.plan_start).replace(" 08:", " 14:"), plan_end: shift(o.plan_end).replace(" 08:", " 14:") })) });
    route.fulfill({ status: 200, headers: { "access-control-allow-origin": "*", "content-type": "application/json" }, body: JSON.stringify(rows) });
  });
  async function openTrip(index) {
    await p.goto("http://127.0.0.1:3000/?page=gantt"); await p.waitForSelector("svg rect[style*=pointer]", { timeout: 60000 });
    await p.locator("svg rect[style*=pointer]").nth(index).click(); await p.waitForSelector(".gantt-card-actions", { timeout: 15000 });
    return Number((await p.locator(".gantt-card-overlay").innerText()).match(/#?(\d{5})/)?.[1] || 0);
  }
  const zone = (z) => p.locator('select[aria-label="Часовой пояс плановых дат"]').selectOption(z);
  const banner = () => p.locator('[aria-label="Незавершённое утверждение времени"]');
  // 1. Утверждение с оборванным ответом.
  const tripA = await openTrip(0); res.tripA = tripA;
  await zone("Europe/Moscow"); await p.getByRole("button", { name: "Прочитать актуальный план" }).click();
  await p.waitForSelector('input[aria-label="Основание утверждения времени"]', { timeout: 20000 });
  await p.fill('input[aria-label="Основание утверждения времени"]', "MOCK C0032 recovery reason");
  await p.getByLabel("Проверить время после полной подтверждённой погрузки").check();
  await p.getByRole("button", { name: "Утвердить маршрут и время" }).click(); await p.waitForTimeout(800);
  res.unknown = { message: await p.locator(".gantt-card-actions p[role=status]").last().textContent(), stored: await p.evaluate((k) => localStorage.getItem(k), KEY), posts: posts.length };
  // 2. Перезагрузка: баннер и восстановленные поля.
  await p.reload(); const again = await openTrip(0); await zone("Europe/Moscow"); await banner().waitFor({ timeout: 10000 });
  res.afterReload = { trip: again, banner: (await banner().innerText()).replace(/\s+/g, " "), retryVisible: await p.getByRole("button", { name: "Повторить сохранённое утверждение" }).isVisible() };
  await p.getByRole("button", { name: "Прочитать актуальный план" }).click(); await p.waitForSelector('input[aria-label="Основание утверждения времени"]', { timeout: 20000 });
  res.restoredFields = { reason: await p.inputValue('input[aria-label="Основание утверждения времени"]'), loadedReview: await p.getByLabel("Проверить время после полной подтверждённой погрузки").isChecked(),
    approveDisabled: await p.getByRole("button", { name: "Утвердить маршрут и время" }).isDisabled(), reasonDisabled: await p.isDisabled('input[aria-label="Основание утверждения времени"]') };
  await p.locator(".gantt-card-actions").screenshot({ path: `${OUT}/c1_pending_after_reload.png` });
  // 3. Другой часовой пояс — только подсказка, без отправки.
  await zone("Asia/Tbilisi"); await banner().waitFor(); res.otherZone = (await banner().innerText()).replace(/\s+/g, " ").slice(-140);
  // 4. Другой рейс — команда не отправляется от текущего рейса.
  const count = await p.locator("svg rect[style*=pointer]").count(); let tripB = again, idx = 1;
  while (tripB === again && idx < count) { tripB = await openTrip(idx); idx++; }
  if (tripB !== again) { await zone("Europe/Moscow"); await banner().waitFor(); res.otherTrip = { trip: tripB, text: (await banner().innerText()).replace(/\s+/g, " ").slice(-200), retryVisible: await p.getByRole("button", { name: "Повторить сохранённое утверждение" }).count() }; }
  // 5. Исходный рейс и пояс: повтор того же тела, успешный ответ.
  mode = "ok"; await openTrip(0); await zone("Europe/Moscow"); await banner().waitFor();
  await p.getByRole("button", { name: "Повторить сохранённое утверждение" }).click();
  await p.waitForFunction(() => /Решение сохранено/.test(document.querySelector(".gantt-card-actions")?.textContent || ""), null, { timeout: 15000 });
  res.retry = { posts: posts.length, sameBody: JSON.stringify(posts[0]) === JSON.stringify(posts[posts.length - 1]), cleared: await p.evaluate((k) => localStorage.getItem(k), KEY) === null,
    body: posts[0] && { trip: posts[0].trip_id, zone: posts[0].time_zone, phase: posts[0].approval_phase, version: posts[0].expected_version } };
  await p.locator(".gantt-card-actions").screenshot({ path: `${OUT}/c2_retry_saved.png` });
  // 6. Повреждённая запись блокирует новое утверждение.
  await p.evaluate((k) => localStorage.setItem(k, "{broken"), KEY); await openTrip(0); await zone("Europe/Moscow");
  await p.waitForFunction(() => /повреждена/.test(document.querySelector(".gantt-card-actions")?.textContent || ""), null, { timeout: 10000 });
  await p.getByRole("button", { name: "Прочитать актуальный план" }).click(); await p.waitForSelector('input[aria-label="Основание утверждения времени"]', { timeout: 20000 });
  res.damaged = { text: (await p.locator(".gantt-card-actions [role=status]").first().innerText()).replace(/\s+/g, " ").slice(0, 160), approveDisabled: await p.getByRole("button", { name: "Утвердить маршрут и время" }).isDisabled() };
  await p.evaluate((k) => localStorage.removeItem(k), KEY);
  fs.writeFileSync(`${OUT}/../c0032_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
