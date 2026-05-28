const { chromium } = require("playwright");

const APP_URL = process.env.WMS_UI_URL || "http://127.0.0.1:3000/?page=transport";

const rows = [
  {
    ST_NUMBER: "ДЦСТ-П00001",
    ADDR: "Добра Цен #П01 г.Пермь ул.Ленина 10",
    REGION: "г. Пермь",
    RAION: "Дзержинский",
    ORD: 1,
    TRANSPORT_TYPE: "10",
    NEEDS_HYDRO_BOARD: 0,
    STOL: 0,
    PRIM1: "до 18:00",
    WARE_ID: 9201,
    NAPR: "Пермь",
    PALLETS_COUNT: 4,
    WEIGHT_KG: 1200,
    VOLUME_M3: 3.2,
    STDATE: "2026-05-25T00:00:00",
    DATE_LOAD: "2026-05-25T00:00:00",
    TRANSTASK_ID: null,
    VERIFY_PERC: 100,
    SUGAR: 0
  },
  {
    ST_NUMBER: "ДЦСТ-П00002",
    ADDR: "Добра Цен #П02 г.Пермь ул.Мира 20",
    REGION: "г. Пермь",
    RAION: "Индустриальный",
    ORD: 2,
    TRANSPORT_TYPE: "15",
    NEEDS_HYDRO_BOARD: 1,
    STOL: 1,
    PRIM1: "стол",
    WARE_ID: 9202,
    NAPR: "Пермь",
    PALLETS_COUNT: 2,
    WEIGHT_KG: 600,
    VOLUME_M3: 1.1,
    STDATE: "2026-05-25T00:00:00",
    DATE_LOAD: "2026-05-25T00:00:00",
    TRANSTASK_ID: null,
    VERIFY_PERC: 0,
    SUGAR: 1
  }
];

function filterRows(url) {
  const parsed = new URL(url);
  let result = rows.slice();
  const transportType = parsed.searchParams.get("transport_type");
  const addrMask = parsed.searchParams.get("addr_mask");
  const stMask = parsed.searchParams.get("st_mask");
  const exclude = parsed.searchParams.get("st_mask_exclude") === "true";
  const assembledOnly = parsed.searchParams.get("assembled_only") === "true";
  const notAssembledOnly = parsed.searchParams.get("not_assembled_only") === "true";
  if (transportType) result = result.filter((row) => row.TRANSPORT_TYPE === transportType);
  if (addrMask) result = result.filter((row) => `${row.ADDR} ${row.REGION} ${row.RAION}`.includes(addrMask));
  if (stMask) {
    result = result.filter((row) => {
      const match = row.ST_NUMBER.toLowerCase().includes(stMask.toLowerCase());
      return exclude ? !match : match;
    });
  }
  if (assembledOnly) result = result.filter((row) => row.VERIFY_PERC > 0);
  if (notAssembledOnly) result = result.filter((row) => !row.VERIFY_PERC);
  return result;
}

async function installMocks(page, calls) {
  await page.route("**/api/admin/transport/vehicles", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/drivers", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/types", (route) => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify([
      { TRANSPORTTYPE: "10", NAME: "Тент 10т" },
      { TRANSPORTTYPE: "15", NAME: "Тент 15т" }
    ])
  }));
  await page.route("**/api/admin/transport/tasks?**", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
  await page.route("**/api/admin/transport/available-sts?**", (route) => {
    calls.available.push(route.request().url());
    route.fulfill({ contentType: "application/json", body: JSON.stringify(filterRows(route.request().url())) });
  });
  await page.route("**/api/admin/transport/clusters?**", (route) => route.fulfill({ contentType: "application/json", body: "[]" }));
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const calls = { available: [] };
  await installMocks(page, calls);

  const started = Date.now();
  await page.goto(APP_URL);
  await page.getByRole("heading", { name: "Диспетчер отгрузки" }).waitFor({ timeout: 10000 });
  await page.getByText("ДЦСТ-П00001").waitFor({ timeout: 10000 });
  const firstPaintMs = Date.now() - started;
  assert(firstPaintMs < 3000, `Sprint 1 UI first table render too slow: ${firstPaintMs}ms`);

  for (const header of ["Скл", "Пал.", "Вес", "Объём", "Регион", "Адрес", "СТ №", "В рейсе", "Дата СТ", "%", "Район", "Тип ТС", "Стол", "Прим.", "Полнопал."]) {
    await page.locator("th", { hasText: header }).first().waitFor({ timeout: 5000 });
  }

  const firstRequestCheckbox = page.locator(".dispatch-grid tbody input[type='checkbox']").first();
  await firstRequestCheckbox.check();
  await firstRequestCheckbox.waitFor({ state: "attached", timeout: 5000 });
  await page.locator(".dispatch-sel-bar-stat", { hasText: "P=4" }).waitFor({ timeout: 5000 });

  await page.locator(".dispatch-fp-select").selectOption("15");
  await page.getByText("ДЦСТ-П00002").waitFor({ timeout: 5000 });
  assert(!(await page.getByText("ДЦСТ-П00001").isVisible()), "Transport type filter did not hide type 10 row");

  await page.locator(".dispatch-fp-select").selectOption("");
  await page.getByPlaceholder("Адрес / регион").fill("Индустриальный");
  await page.waitForTimeout(450);
  await page.getByText("ДЦСТ-П00002").waitFor({ timeout: 5000 });

  await page.getByPlaceholder(/Номер СТ/).fill("ДЦСТ-П00001");
  await page.waitForTimeout(450);
  assert(calls.available.some((url) => url.includes("st_mask=")), "ST mask was not sent to API");

  await browser.close();
  console.log(JSON.stringify({ ok: true, firstPaintMs, availableCalls: calls.available.length }));
}

main().catch(async (error) => {
  console.error(error);
  process.exit(1);
});
