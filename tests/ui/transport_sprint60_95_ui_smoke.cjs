const path = require("path");
const { createRequire } = require("module");
const { pageUrl } = require("../support/project_config.cjs");

function requirePlaywright() {
  try {
    return require("playwright");
  } catch {
    return createRequire(path.resolve("admin/wms_admin_frontend/package.json"))("playwright");
  }
}

const { chromium } = requirePlaywright();
const APP_URL = process.env.WMS_UI_URL || pageUrl("transport");

const tasks = [
  {
    ID: 9101,
    TRANSTYPE: "Тент",
    TRANSPORT: "Е715ТТ",
    VODITEL_ID: 1,
    VODITEL_NAME: "Иванов И.И.",
    REGIONS: "Пермь",
    TK_NAME: "ООО Ромашка",
    LOGIST: "Логист А",
    DOCK: "Д-1",
    SHIPMENT_DATE: "2026-05-25",
    SHIPMENT_TIME: "09:00",
    CONDITION: "Новый",
    ST_COUNT: 3,
    PALLET_COUNT: 12,
    TEMP_WEIGHT: 900,
    VOLUME_M3: 5.5,
    PRICE: 0,
    PAY_ORDER_ID: null,
    DELETED: 0,
    READY_PERC: 67,
    UNREADY_COUNT: 1,
    PRIMECHANIE: "Проверить температурный режим",
  },
  {
    ID: 9102,
    TRANSTYPE: "Реф",
    TRANSPORT: "А123БВ",
    VODITEL_ID: 2,
    VODITEL_NAME: "Петров П.П.",
    REGIONS: "Лысьва",
    TK_NAME: "ООО Березка",
    LOGIST: "Логист Б",
    DOCK: "Д-2",
    SHIPMENT_DATE: "2026-05-25",
    SHIPMENT_TIME: "10:30",
    CONDITION: "Новый",
    ST_COUNT: 0,
    PALLET_COUNT: 0,
    TEMP_WEIGHT: 0,
    VOLUME_M3: 0,
    PRICE: 0,
    PAY_ORDER_ID: null,
    DELETED: 0,
    READY_PERC: 100,
    UNREADY_COUNT: 0,
    PRIMECHANIE: null,
  },
  {
    ID: 9103,
    TRANSTYPE: "Изо",
    TRANSPORT: "В456ГД",
    VODITEL_ID: 3,
    VODITEL_NAME: "Сидоров С.С.",
    REGIONS: "Чусовой",
    TK_NAME: "ООО Север",
    LOGIST: "Логист В",
    DOCK: "Д-3",
    SHIPMENT_DATE: "2026-05-25",
    SHIPMENT_TIME: "11:00",
    CONDITION: "Отгружен",
    ST_COUNT: 1,
    PALLET_COUNT: 2,
    TEMP_WEIGHT: 150,
    VOLUME_M3: 1.25,
    PRICE: 0,
    PAY_ORDER_ID: null,
    DELETED: 0,
    READY_PERC: 100,
    UNREADY_COUNT: 0,
    PRIMECHANIE: null,
  },
];

const availableSts = [
  {
    ST_NUMBER: "AV-ST-001",
    ADDR: "ул. Ленина 1",
    REGION: "Пермь",
    RAION: "Центр",
    ORD: 1,
    TRANSPORT_TYPE: "Тент",
    WARE_ID: 9201,
    NAPR: "Север",
    PALLETS_COUNT: 5,
    WEIGHT_KG: 300,
    VOLUME_M3: 2.5,
    STDATE: "2026-05-25T00:00:00",
    DATE_LOAD: "2026-05-25T00:00:00",
    TRANSTASK_ID: null,
    VERIFY_PERC: 100,
    SUGAR: 0,
  },
  {
    ST_NUMBER: "AV-ST-002",
    ADDR: "пр. Мира 10",
    REGION: "Лысьва",
    RAION: "Запад",
    ORD: 2,
    TRANSPORT_TYPE: "Реф",
    WARE_ID: 9202,
    NAPR: "Юг",
    PALLETS_COUNT: 8,
    WEIGHT_KG: 500,
    VOLUME_M3: 3.0,
    STDATE: "2026-05-25T00:00:00",
    DATE_LOAD: "2026-05-25T00:00:00",
    TRANSTASK_ID: null,
    VERIFY_PERC: 50,
    SUGAR: 0,
  },
  {
    ST_NUMBER: "AV-ST-003",
    ADDR: "ул. Складская 3",
    REGION: "Чусовой",
    RAION: "Восток",
    ORD: 3,
    TRANSPORT_TYPE: "Изо",
    WARE_ID: 9201,
    NAPR: "Восток",
    PALLETS_COUNT: 2,
    WEIGHT_KG: 100,
    VOLUME_M3: 1.0,
    STDATE: "2026-05-25T00:00:00",
    DATE_LOAD: "2026-05-25T00:00:00",
    TRANSTASK_ID: null,
    VERIFY_PERC: null,
    SUGAR: 1,
  },
];

const taskSts = [
  {
    ST_NUMBER: "TRIP-ST-A",
    ADDR: "Адрес A",
    REGION: "Пермь",
    RAION: "Центр",
    ORD: 2,
    TRANSPORT_TYPE: "Тент",
    WARE_ID: 9201,
    PALLETS_COUNT: 4,
    WEIGHT_KG: 300,
    VOLUME_M3: 1.5,
    VERIFY_PERC: 100,
    ZONE: "Z1",
    TIME_FROM: "10:00",
    TIME_TO: "11:00",
    LOAD_TYPE: "Г",
  },
  {
    ST_NUMBER: "TRIP-ST-B",
    ADDR: "Адрес B",
    REGION: "Лысьва",
    RAION: "Запад",
    ORD: 1,
    TRANSPORT_TYPE: "Реф",
    WARE_ID: 9202,
    PALLETS_COUNT: 6,
    WEIGHT_KG: 450,
    VOLUME_M3: 2.75,
    VERIFY_PERC: 40,
    ZONE: "Z2",
    TIME_FROM: "08:00",
    TIME_TO: "09:00",
    LOAD_TYPE: "П",
  },
  {
    ST_NUMBER: "TRIP-ST-C",
    ADDR: "Адрес C",
    REGION: "Чусовой",
    RAION: "Восток",
    ORD: 3,
    TRANSPORT_TYPE: "Изо",
    WARE_ID: 9201,
    PALLETS_COUNT: 2,
    WEIGHT_KG: 150,
    VOLUME_M3: 1.25,
    VERIFY_PERC: 100,
    ZONE: "Z3",
    TIME_FROM: "12:00",
    TIME_TO: "13:00",
    LOAD_TYPE: "",
  },
];

const emptyTaskSts = [];
let assignPayload = null;
let unassignedSt = null;
let patchedTask = null;
let closeCalled = false;

async function installMocks(context) {
  await context.route("**/api/admin/transport/vehicles", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await context.route("**/api/admin/transport/drivers", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await context.route("**/api/admin/transport/types", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await context.route("**/api/admin/transport/billing/orders?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await context.route("**/api/admin/transport/clusters?**", route => route.fulfill({ contentType: "application/json", body: "[]" }));
  await context.route("**/api/admin/transport/available-sts?**", route => route.fulfill({ contentType: "application/json", body: JSON.stringify(availableSts) }));
  await context.route(/\/api\/admin\/transport\/tasks(?:\?|$)/, route => route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks) }));
  await context.route(/\/api\/admin\/transport\/tasks\/9101\/sts$/, async route => {
    if (route.request().method() === "POST") {
      assignPayload = JSON.parse(route.request().postData() || "{}");
      await route.fulfill({ contentType: "application/json", body: JSON.stringify({ assigned: assignPayload.st_numbers.length, warnings: [] }) });
      return;
    }
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(taskSts) });
  });
  await context.route(/\/api\/admin\/transport\/tasks\/9102\/sts$/, route => route.fulfill({ contentType: "application/json", body: JSON.stringify(emptyTaskSts) }));
  await context.route(/\/api\/admin\/transport\/tasks\/9101\/sts\/([^/]+)$/, route => {
    unassignedSt = decodeURIComponent(route.request().url().split("/").pop());
    return route.fulfill({ contentType: "application/json", body: JSON.stringify({ ok: true }) });
  });
  await context.route(/\/api\/admin\/transport\/tasks\/9101\/close$/, route => {
    closeCalled = true;
    return route.fulfill({ contentType: "application/json", body: JSON.stringify({ ok: true }) });
  });
  await context.route(/\/api\/admin\/transport\/tasks\/9101$/, async route => {
    if (route.request().method() === "PATCH") {
      patchedTask = JSON.parse(route.request().postData() || "{}");
      await route.fulfill({ contentType: "application/json", body: JSON.stringify({ ...tasks[0], ...patchedTask }) });
      return;
    }
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(tasks[0]) });
  });
}

async function assertVisible(locator, label) {
  if (!(await locator.first().isVisible())) throw new Error(`${label} is not visible`);
}

async function rowTexts(locator) {
  return locator.evaluateAll(rows => rows.map(row => row.innerText));
}

async function main() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ acceptDownloads: true, viewport: { width: 1440, height: 930 } });
  await installMocks(context);
  const page = await context.newPage();
  await page.addInitScript(() => {
    localStorage.setItem("tms_activeTab", "tasks");
    localStorage.setItem("tms_viewMode", "flat");
    localStorage.setItem("tms_stDate", "2026-05-25");
    localStorage.setItem("tms_filterDate", "2026-05-25");
    localStorage.setItem("tms_routeShipDate", "2026-05-25");
    Object.defineProperty(navigator, "clipboard", {
      value: {
        writeText: async text => { window.__copiedText = text; },
      },
      configurable: true,
    });
  });
  await page.goto(APP_URL);
  await page.locator(".dispatch-tab.active", { hasText: "Заявки" }).waitFor({ timeout: 10000 });
  await page.getByText("AV-ST-001").waitFor({ timeout: 10000 });

  // Sprint 60 / 102 current contract: table is bounded by virtualization, not by DOM-heavy paging.
  await page.locator(".dispatch-page-info", { hasText: "виртуализация активна" }).waitFor({ timeout: 5000 });

  // Sprint 61, 80, 83: warehouse filter, NAPR and unready border in available ST table.
  await assertVisible(page.locator(".dispatch-napr-badge", { hasText: "Север" }), "NAPR badge");
  await page.locator(".dispatch-ware-select").selectOption("9202");
  await page.getByText("AV-ST-002").waitFor({ timeout: 5000 });
  if (await page.getByText("AV-ST-001").isVisible()) throw new Error("warehouse filter did not hide WARE_ID 9201 row");
  await assertVisible(page.locator(".dispatch-avail-unready", { hasText: "AV-ST-002" }), "available unready row");
  await page.locator(".dispatch-ware-select").selectOption("");

  // Sprint 62: sticky headers exist on both ST and route tables.
  const stHeaderPosition = await page.locator(".dispatch-st-section thead th").first().evaluate(el => getComputedStyle(el).position);
  if (stHeaderPosition !== "sticky") throw new Error(`ST header is not sticky: ${stHeaderPosition}`);

  // Sprint 63-65: unready badge selects unready rows and updates tab badge.
  await page.locator(".dispatch-notready-select-btn").click();
  await page.locator(".dispatch-sel-bar-count", { hasText: "1 выбр." }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-tab-badge", { hasText: "1" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-ds-empty-warn", { hasText: "пуст" }).waitFor({ timeout: 5000 });

  // Sprint 68: Ctrl+Enter assigns selected available STs to selected trip.
  await page.locator('.dispatch-trips-table-wrap tbody tr[data-taskid="9101"]').click();
  await page.locator(".dispatch-trip-detail-section", { hasText: "Рейс #9101" }).waitFor({ timeout: 5000 });
  await page.keyboard.press("Control+Enter");
  if (!assignPayload || assignPayload.st_numbers[0] !== "AV-ST-002") {
    throw new Error(`Ctrl+Enter assign payload mismatch: ${JSON.stringify(assignPayload)}`);
  }

  // Sprint 66-67, 70, 72, 75-77, 89-92: trip composition controls.
  await page.locator(".dispatch-trip-sts-wrap th", { hasText: "%" }).waitFor({ timeout: 5000 });
  await assertVisible(page.locator(".dispatch-verify-bar", { hasText: "40%" }), "trip verify bar");
  await assertVisible(page.locator(".dispatch-gr-unready", { hasText: "TRIP-ST-B" }), "trip unready row");
  await page.locator(".dispatch-pmv", { hasText: "V=" }).first().waitFor({ timeout: 5000 });
  await page.locator(".dispatch-trip-selall-btn", { hasText: "Все" }).click();
  await page.locator(".dispatch-trip-bulk-bar", { hasText: "3 СТ выбрано" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-trip-selall-btn", { hasText: "Нет" }).click();
  await page.locator(".dispatch-trip-filter-input").fill("TRIP-ST-B");
  await page.locator(".dispatch-trip-sts-count", { hasText: "1 / 3" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-trip-filter-clear").click();
  await page.locator(".dispatch-trip-unready-btn").click();
  await page.locator(".dispatch-trip-sts-count", { hasText: "1 / 3" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-trip-unready-btn").click();
  await page.locator(".dispatch-trip-timesort-btn").click();
  const sortedRows = await rowTexts(page.locator(".dispatch-trip-sts-wrap tbody tr.dispatch-gr"));
  if (!sortedRows[0].includes("TRIP-ST-B")) throw new Error(`time sort did not put earliest ST first: ${JSON.stringify(sortedRows)}`);
  await page.locator(".dispatch-trip-copy-sts-btn").click();
  const copiedAll = await page.evaluate(() => window.__copiedText);
  if (!copiedAll.includes("TRIP-ST-B") || !copiedAll.includes("TRIP-ST-A")) {
    throw new Error(`copy-all ST payload mismatch: ${JSON.stringify(copiedAll)}`);
  }
  const [tripCsv] = await Promise.all([
    page.waitForEvent("download"),
    page.locator(".dispatch-trip-csv-btn").click(),
  ]);
  if (tripCsv.suggestedFilename() !== "trip-9101-sts.csv") throw new Error(`unexpected trip CSV filename: ${tripCsv.suggestedFilename()}`);

  // Sprint 69 and 90: Delete shortcut unassigns selected ST; ST number cell copies to clipboard.
  await page.locator(".dispatch-trip-selall-btn", { hasText: "Нет" }).click().catch(() => {});
  await page.locator(".dispatch-trip-sts-wrap tbody tr", { hasText: "TRIP-ST-B" }).locator("input[type='checkbox']").check();
  await page.locator(".dispatch-trip-bulk-bar", { hasText: "1 СТ выбрано" }).waitFor({ timeout: 5000 });
  page.once("dialog", async dialog => {
    if (!dialog.message().includes("Снять 1 СТ")) throw new Error(`unexpected bulk-unassign dialog: ${dialog.message()}`);
    await dialog.accept();
  });
  await page.keyboard.press("Delete");
  if (unassignedSt !== "TRIP-ST-B") throw new Error(`Delete shortcut unassigned ${unassignedSt}`);
  await page.locator(".dispatch-st-copy-cell", { hasText: "TRIP-ST-A" }).first().click();
  const copiedOne = await page.evaluate(() => window.__copiedText);
  if (copiedOne !== "TRIP-ST-A") throw new Error(`single ST copy mismatch: ${copiedOne}`);

  // Sprint 74, 87, 88: collapse, reschedule, close warning.
  await page.locator(".dispatch-trip-collapse-btn").click();
  await page.locator(".dispatch-trip-sts-wrap").waitFor({ state: "hidden", timeout: 5000 });
  await page.locator(".dispatch-trip-collapse-btn").click();
  page.once("dialog", async dialog => {
    if (!dialog.message().includes("Перенести рейс")) throw new Error(`unexpected reschedule dialog: ${dialog.message()}`);
    await dialog.accept();
  });
  await page.locator(".dispatch-reschedule-btn").click();
  if (!patchedTask || patchedTask.shipment_date !== "2026-05-26") {
    throw new Error(`reschedule payload mismatch: ${JSON.stringify(patchedTask)}`);
  }
  page.once("dialog", async dialog => {
    if (!dialog.message().includes("не полностью собраны")) throw new Error(`close warning does not mention unready STs: ${dialog.message()}`);
    await dialog.accept();
  });
  await page.locator(".dispatch-close-btn").click();
  if (!closeCalled) throw new Error("close endpoint was not called");

  // Sprint 71, 73, 79, 84-86, 93-95: routes tab columns, summary, empty warning, note tooltip.
  await page.locator(".dispatch-tab", { hasText: "Маршруты" }).click();
  await page.locator(".dispatch-routes-table-wrap tbody tr[data-taskid='9101']").waitFor({ timeout: 5000 });
  const routeHeaderPosition = await page.locator(".dispatch-routes-table-wrap thead th").first().evaluate(el => getComputedStyle(el).position);
  if (routeHeaderPosition !== "sticky") throw new Error(`routes header is not sticky: ${routeHeaderPosition}`);
  await page.locator(".dispatch-routes-table-wrap th", { hasText: "ТК" }).waitFor({ timeout: 5000 });
  await page.locator(".dispatch-routes-table-wrap th", { hasText: "Логист" }).waitFor({ timeout: 5000 });
  await assertVisible(page.locator(".dispatch-readiness", { hasText: "67%" }), "route readiness");
  await page.locator(".dispatch-routes-summary", { hasText: "Рейсов:" }).waitFor({ timeout: 5000 });
  await assertVisible(page.locator(".dispatch-routes-table-wrap .dispatch-trip-unready", { hasText: "9101" }), "route unready border");
  const noteTitle = await page.locator(".dispatch-routes-table-wrap tbody tr[data-taskid='9101']").getAttribute("title");
  if (!noteTitle || !noteTitle.includes("Проверить температурный режим")) throw new Error(`missing note tooltip: ${noteTitle}`);
  const [routesCsv] = await Promise.all([
    page.waitForEvent("download"),
    page.locator(".dispatch-trip-csv-btn").first().click(),
  ]);
  if (!routesCsv.suggestedFilename().startsWith("routes-")) throw new Error(`unexpected routes CSV filename: ${routesCsv.suggestedFilename()}`);

  // Sprint 81: keyboard navigation in routes tab moves selected trip.
  await page.locator(".dispatch-routes-table-wrap tbody tr[data-taskid='9101']").click();
  await page.keyboard.press("ArrowDown");
  await page.locator(".dispatch-trip-detail-section", { hasText: "Рейс #9102" }).waitFor({ timeout: 5000 });

  await browser.close();
  console.log(JSON.stringify({ ok: true, covered: "sprint60-95" }));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
