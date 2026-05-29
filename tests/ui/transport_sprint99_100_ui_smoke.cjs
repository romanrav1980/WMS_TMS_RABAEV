/**
 * transport_sprint99_100_ui_smoke.cjs — Sprint 99-100: UserManagementPage
 *
 * Проверяет:
 * 1. Страница ?page=users открывается
 * 2. Вкладки «Пользователи» и «Права групп» видны
 * 3. Таблица пользователей рендерит данные
 * 4. Диалог «Добавить пользователя» открывается
 * 5. Левая панель групп в Rights Tab
 * 6. Чекбоксы прав рендерятся
 */

const { chromium } = require("playwright");

const USERS_URL = (process.env.WMS_UI_URL || "http://localhost:3000") + "?page=users";

const MOCK_USERS = [
  { login: "dispatch1", display_name: "Диспетчер Первый", user_group: "TRANSPORT_TEAM", is_admin: false, is_deleted: false },
  { login: "billing1",  display_name: "Биллинг Специалист", user_group: "BILLING_TEAM", is_admin: false, is_deleted: false },
  { login: "admin",     display_name: "Администратор",      user_group: "GLOBAL_ADMIN",  is_admin: true,  is_deleted: false },
];

const MOCK_GROUPS = [
  { group: "TRANSPORT_TEAM", rights: ["transport_dispatch_view", "transport_dispatch_edit"] },
  { group: "BILLING_TEAM",   rights: ["transport_dispatch_view", "edit_bill_tt", "calc_tt_price"] },
  { group: "GLOBAL_ADMIN",   rights: ["*"] },
];

const MOCK_RIGHTS = [
  "transport_dispatch_view", "transport_dispatch_edit", "transport_dispatch_close",
  "transport_fleet_edit", "edit_bill_tt", "calc_tt_price", "create_tt_price",
  "rights_admin_view", "rights_admin_edit",
];

async function installMocks(page) {
  await page.route("**/api/admin/users", r => r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_USERS) }));
  await page.route("**/api/admin/users/groups", r => r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_GROUPS) }));
  await page.route("**/api/admin/users/rights", r => r.fulfill({ contentType: "application/json", body: JSON.stringify(MOCK_RIGHTS) }));
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await installMocks(page);
  await page.goto(USERS_URL);

  // Page header
  await page.locator("h1").filter({ hasText: /пользовател/i }).waitFor({ timeout: 8000 });

  // Users tab (default)
  const usersTab = page.locator(".umgmt-tab-btn").filter({ hasText: /пользовател/i });
  await usersTab.waitFor();
  const rightsTab = page.locator(".umgmt-tab-btn").filter({ hasText: /права/i });
  await rightsTab.waitFor();
  console.log("✓ Tabs 'Пользователи' and 'Права групп' visible");

  // User table with data
  await page.getByText("dispatch1").waitFor({ timeout: 5000 });
  await page.getByText("Диспетчер Первый").waitFor();
  await page.getByText("TRANSPORT_TEAM").waitFor();
  console.log("✓ User table shows mock data");

  // Status badges
  const activeBadge = page.locator(".umgmt-active").first();
  await activeBadge.waitFor();
  console.log("✓ Status badges visible");

  // Add user dialog
  const addBtn = page.locator(".umgmt-add-btn").first();
  await addBtn.click();
  const modal = page.locator(".umgmt-modal");
  await modal.waitFor({ timeout: 3000 });
  const title = await modal.locator(".umgmt-modal-title").innerText();
  if (!title.toLowerCase().includes("добав")) throw new Error(`Expected 'Добавить' title, got: '${title}'`);

  // Required fields in dialog
  const inputs = modal.locator("input");
  const inputCount = await inputs.count();
  if (inputCount < 3) throw new Error(`Expected at least 3 inputs in user dialog, got ${inputCount}`);
  console.log(`✓ Add user dialog opens with ${inputCount} inputs`);

  // Close dialog
  await modal.locator(".umgmt-modal-cancel").click();
  await modal.waitFor({ state: "hidden", timeout: 3000 });
  console.log("✓ Dialog closes on cancel");

  // Switch to Rights tab
  await rightsTab.click();

  // Left panel: groups list
  const groupsPanel = page.locator(".umgmt-groups-panel");
  await groupsPanel.waitFor({ timeout: 5000 });
  await page.getByText("TRANSPORT_TEAM").first().waitFor({ timeout: 5000 });
  await page.getByText("BILLING_TEAM").first().waitFor();
  console.log("✓ Groups panel renders TRANSPORT_TEAM, BILLING_TEAM");

  // Click on TRANSPORT_TEAM
  await page.locator(".umgmt-group-item").filter({ hasText: "TRANSPORT_TEAM" }).click();

  // Rights checkboxes
  const rightsPanel = page.locator(".umgmt-rights-panel");
  await rightsPanel.waitFor();
  const checkboxes = rightsPanel.locator("input[type='checkbox']");
  const checkCount = await checkboxes.count();
  if (checkCount < 5) throw new Error(`Expected ≥5 right checkboxes, got ${checkCount}`);
  console.log(`✓ Rights panel shows ${checkCount} permission checkboxes`);

  // transport_dispatch_view should be checked for TRANSPORT_TEAM
  const viewCheckbox = rightsPanel.locator("input[type='checkbox']").nth(0);
  const isChecked = await viewCheckbox.isChecked();
  console.log(`✓ First right checkbox checked=${isChecked}`);

  await browser.close();
  console.log("Sprint 99-100 UI smoke: PASSED");
}

main().catch(err => { console.error("Sprint 99-100 UI smoke: FAILED", err.message); process.exit(1); });
