const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const store = {
  availableSts: [
    { ST_NUMBER: "ДЦСТ-П13001", ADDR: "Адрес Sprint 13", REGION: "Пермь", RAION: "Центр", ORD: 1, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: "", WARE_ID: 9201, NAPR: "Пермь", PALLETS_COUNT: 4, WEIGHT_KG: 1000, VOLUME_M3: 3.1, STDATE: "2026-05-25T00:00:00", DATE_LOAD: "2026-05-25T00:00:00", TRANSTASK_ID: null, VERIFY_PERC: 100, SUGAR: 0 },
  ],
  vehicles: [
    { ID: 1, NUM: "А 100 АА 59", MARKA: "Газель", TR_TYPE: "5", PALLETS: 8, GIDROBORT: 0 },
    { ID: 2, NUM: "В 200 ВВ 59", MARKA: "Тент", TR_TYPE: "10", PALLETS: 18, GIDROBORT: 1 },
    { ID: 3, NUM: "С 300 СС 59", MARKA: "Фура", TR_TYPE: "20", PALLETS: 33, GIDROBORT: 0 },
  ],
  availability: [
    { vehicle_id: 1, vehicle_num: "А 100 АА 59", vehicle_type: "5", marka: "Газель", max_pallets: 8, gidrobort: false, free_at: null, delay_min: 0, status: "green", detail: "Свободна" },
    { vehicle_id: 2, vehicle_num: "В 200 ВВ 59", vehicle_type: "10", marka: "Тент", max_pallets: 18, gidrobort: true, free_at: "09:35", delay_min: 35, status: "yellow", detail: "Освободится в 09:35" },
    { vehicle_id: 3, vehicle_num: "С 300 СС 59", vehicle_type: "20", marka: "Фура", max_pallets: 33, gidrobort: false, free_at: "12:30", delay_min: 210, status: "red", detail: "Занята до 12:30" },
  ],
  calls: { availability: 0 },
};

async function installMocks(page) {
  await page.route("**/api/admin/transport/vehicles/available?**", (route) => {
    store.calls.availability += 1;
    route.fulfill({ contentType: "application/json", body: JSON.stringify(store.availability) });
  });
  await page.route("**/api/admin/transport/vehicles", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify(store.vehicles) }));
  await page.route("**/api/admin/transport/drivers", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify([{ TRANSPORTTYPE: "10", NAME: "Тент 10т" }]) }));
  await page.route("**/api/admin/transport/available-sts?**", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify(store.availableSts) }));
  await page.route("**/api/admin/transport/tasks?**", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);

  await page.goto(APP_URL);
  await page.getByText("ДЦСТ-П13001").waitFor({ timeout: 10000 });
  await page.locator(".dispatch-grid tbody input[type='checkbox']").first().check();
  await page.getByText("+ Создать маршрут (1)").click();
  await page.getByRole("heading", { name: /Создать маршрут/ }).waitFor({ timeout: 5000 });

  const vehicleSelect = page.locator(".dispatch-dialog-field", { hasText: "Машина" }).locator("select");
  await vehicleSelect.waitFor({ timeout: 5000 });
  await page.waitForFunction(() => {
    const select = [...document.querySelectorAll("select")].find((node) => node.textContent.includes("А 100 АА 59"));
    return select && select.textContent.includes("🟢") && select.textContent.includes("🟡") && select.textContent.includes("🔴");
  }, null, { timeout: 5000 });

  await vehicleSelect.selectOption("С 300 СС 59");
  await page.getByText("Занята до 12:30 — конфликт возможен").waitFor({ timeout: 5000 });
  await vehicleSelect.selectOption("В 200 ВВ 59");
  await page.getByText("Освободится в 09:35").waitFor({ timeout: 5000 });

  if (store.calls.availability < 1) {
    throw new Error("Availability endpoint was not called");
  }

  await browser.close();
  console.log(JSON.stringify({ ok: true, availabilityCalls: store.calls.availability }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
