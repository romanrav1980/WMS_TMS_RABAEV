const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const store = {
  available: [
    { ST_NUMBER: "ДЦСТ-П00001", ADDR: "Адрес 1", REGION: "Пермь", RAION: "Центр", ORD: 1, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: "", WARE_ID: 9201, NAPR: "Пермь", PALLETS_COUNT: 4, WEIGHT_KG: 1000, VOLUME_M3: 3.1, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 100, SUGAR: 0 },
    { ST_NUMBER: "ДЦСТ-П00002", ADDR: "Адрес 2", REGION: "Пермь", RAION: "Центр", ORD: 2, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: "", WARE_ID: 9201, NAPR: "Пермь", PALLETS_COUNT: 2, WEIGHT_KG: 500, VOLUME_M3: 1.5, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 50, SUGAR: 0 }
  ],
  tasks: [],
  taskSts: new Map(),
  calls: { create: [], assign: [] }
};

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify(store.available) }));
  await page.route("**/api/admin/transport/tasks?**", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify(store.tasks) }));
  await page.route(/.*\/api\/admin\/transport\/tasks\/(\d+)$/, (route) => {
    const id = Number(route.request().url().match(/tasks\/(\d+)$/)[1]);
    route.fulfill({ contentType: "application/json", body: JSON.stringify(store.tasks.find((task) => task.ID === id)) });
  });
  await page.route(/.*\/api\/admin\/transport\/tasks\/(\d+)\/sts$/, async (route) => {
    const id = Number(route.request().url().match(/tasks\/(\d+)\/sts$/)[1]);
    if (route.request().method() === "POST") {
      const body = route.request().postDataJSON();
      store.calls.assign.push(body);
      const assigned = store.available.filter((row) => body.st_numbers.includes(row.ST_NUMBER));
      store.taskSts.set(id, assigned);
      store.available = store.available.filter((row) => !body.st_numbers.includes(row.ST_NUMBER));
      route.fulfill({ contentType: "application/json", body: JSON.stringify({ assigned: body.st_numbers.length, warnings: [] }) });
      return;
    }
    route.fulfill({ contentType: "application/json", body: JSON.stringify(store.taskSts.get(id) || []) });
  });
  await page.route("**/api/admin/transport/tasks", async (route) => {
    if (route.request().method() === "POST") {
      const body = route.request().postDataJSON();
      store.calls.create.push(body);
      const task = { ID: 501, TRANSTYPE: body.transtype, SHIPMENT_DATE: `${body.shipment_date}T00:00:00`, CONDITION: "Новый", ST_COUNT: 0, PALLET_COUNT: 0, TEMP_WEIGHT: 0, PRICE: null };
      store.tasks = [task];
      route.fulfill({ contentType: "application/json", body: JSON.stringify({ task_id: 501 }) });
      return;
    }
    route.fallback();
  });
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);

  await page.goto(APP_URL);
  await page.getByText("ДЦСТ-П00001").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-grid tbody input[type='checkbox']").first().check();
  await page.getByText("+ Создать маршрут (1)").click();
  await page.getByRole("heading", { name: /Создать маршрут/ }).waitFor({ timeout: 5000 });
  await page.locator("button", { hasText: "Создать" }).last().click();

  await page.getByText("ДЦСТ-П00001").waitFor({ state: "detached", timeout: 5000 });
  await page.getByText("✓ Рейс #501 создан").waitFor({ timeout: 5000 });
  assert(store.calls.create.length === 1, "Create task API was not called");
  assert(store.calls.assign.length === 1, "Assign selected ST API was not called");
  assert(store.calls.assign[0].st_numbers[0] === "ДЦСТ-П00001", "Wrong ST assigned");

  await browser.close();
  console.log(JSON.stringify({ ok: true, created: store.calls.create.length, assigned: store.calls.assign[0].st_numbers.length }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
