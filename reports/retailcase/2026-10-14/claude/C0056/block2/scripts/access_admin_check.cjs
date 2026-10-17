// C0056 блок 2: AccessAdminPage на реальном /api/access/* (dev preview до интеграции в App).
// Создаёт только тестовые метаданные UI.C0056.*: роль без прав, группу из одного склада, назначение себе (admin) на 1 час
// и сразу отзывает его; роль в конце выключается. Права обычных пользователей не меняются. Пароль читается из AGENTS.md и не печатается.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const URL0 = "http://127.0.0.1:3000/src/features/platform/access-admin/preview/index.html";
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const tag = Date.now().toString(36);
const ROLE = "UI.C0056.ROLE." + tag, GROUP = "UI.C0056.GRP." + tag;
const msg = p => p.locator(".aa-msg").first();

(async () => {
  const b = await chromium.launch(); const res = { posts: [] };
  const page = async (viewport) => {
    const p = await (await b.newContext({ viewport })).newPage();
    p.on("request", r => { if (r.method() !== "GET" && r.url().includes("/api/")) res.posts.push(r.method() + " " + r.url().replace(/^https?:\/\/[^/]+/, "")); });
    await p.goto(URL0);
    await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
    await p.waitForSelector(".aa-meta b", { timeout: 30000 });
    return p;
  };
  const p = await page({ width: 1440, height: 1000 });
  res.meta = (await p.textContent(".aa-meta")).replace(/\s+/g, " ");
  // Клавиатура по вкладкам, tooltip, help_id.
  await p.focus("#aa-tab-assign"); await p.keyboard.press("ArrowRight");
  res.tabAfterArrow = await p.evaluate(() => document.activeElement.id);
  await p.click("#aa-tab-roles");
  const newRole = p.getByRole("button", { name: "Новая роль", exact: true });
  await newRole.hover(); await p.waitForTimeout(200);
  res.tooltipVisible = await p.locator(".help-tooltip").evaluateAll(n => n.filter(x => getComputedStyle(x).display !== "none").map(x => x.textContent));
  res.helpIds = await p.$$eval("[data-help-id]", n => n.length);
  // «?»: открыть, Escape закрывает и возвращает фокус; «Подробнее» открывает статью справки.
  await p.locator(".help-hint-trigger").first().click(); res.hintOpen = await p.locator(".help-hint-panel").count();
  await p.keyboard.press("Escape"); res.hintAfterEscape = await p.locator(".help-hint-panel").count();
  res.focusAfterEscape = await p.evaluate(() => document.activeElement.className);
  await p.locator(".help-hint-trigger").first().click(); await p.getByRole("button", { name: "Подробнее", exact: true }).click();
  await p.waitForSelector("dialog.knowledge-panel[open]", { timeout: 10000 }); await p.waitForTimeout(1000);
  res.helpPanel = (await p.locator(".knowledge-content").innerText()).replace(/\s+/g, " ").slice(0, 200);
  await p.keyboard.press("Escape"); await p.waitForTimeout(300);
  // Роль: недоступное сохранение объясняет причину; затем ROLE_SAVE.
  await newRole.click();
  const save = p.getByRole("button", { name: "Сохранить роль", exact: true });
  res.saveBlockedTitle = await save.getAttribute("title");
  await p.getByLabel("Код роли").fill(ROLE); await p.getByLabel("Название").fill("Проверка UI C0056 (без прав)");
  await save.click(); await p.waitForSelector(".aa-msg", { timeout: 20000 });
  res.roleSaved = await msg(p).textContent();
  await p.screenshot({ path: `${OUT}/a1_roles_desktop.png`, fullPage: true });
  // Группа из одного склада, предпросмотр затронутых назначений, GROUP_SAVE.
  await p.click("#aa-tab-groups"); await p.getByRole("button", { name: "Новая группа", exact: true }).click();
  await p.getByLabel("Код", { exact: true }).fill(GROUP); await p.getByLabel("Название").fill("Проверка UI C0056");
  await p.locator(".aa-picker").getByRole("button", { name: "Найти", exact: true }).click();
  await p.waitForSelector(".aa-picker .aa-list li", { timeout: 20000 });
  await p.locator(".aa-picker .aa-list li").first().getByRole("button", { name: "Добавить", exact: true }).click();
  await p.waitForTimeout(800);
  res.saveBeforeImpact = await p.getByRole("button", { name: "Сохранить группу", exact: true }).getAttribute("title");
  await p.getByRole("button", { name: "Показать влияние", exact: true }).click();
  await p.waitForSelector(".aa-impact", { timeout: 20000 });
  res.impact = (await p.locator(".aa-impact").innerText()).replace(/\s+/g, " ");
  await p.getByRole("button", { name: "Сохранить группу", exact: true }).click();
  await p.waitForFunction(() => /Группа UI/.test(document.querySelector(".aa-msg")?.textContent || ""), null, { timeout: 20000 });
  res.groupSaved = await msg(p).textContent();
  // Назначение себе на 1 час. Первый ответ обрывается после фиксации на сервере → «результат неизвестен».
  await p.click("#aa-tab-assign"); await p.getByRole("button", { name: "Новое назначение", exact: true }).click();
  const form = p.locator(".aa-form").last();
  await form.getByLabel("Пользователь").fill("admin");
  await form.getByLabel("Роль").selectOption(ROLE); await form.getByLabel("Вид области").selectOption("GROUP");
  await form.getByLabel("Группа объектов").selectOption(GROUP);
  const until = new Date(Date.now() + 3600e3 - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  await form.getByLabel("Действует до (не включительно)").fill(until);
  await form.getByLabel("Основание").fill("Проверка UI C0056: роль без прав, будет отозвано");
  let dropped = false;
  await p.route("**/api/access/commands", async route => {
    if (!dropped && route.request().method() === "POST") { dropped = true; await route.fetch(); return route.abort("connectionreset"); }
    return route.continue();
  });
  await form.getByRole("button", { name: "Назначить", exact: true }).click();
  await p.waitForSelector(".aa-pending", { timeout: 20000 });
  res.pendingBanner = (await p.locator(".aa-pending").innerText()).replace(/\s+/g, " ").slice(0, 260);
  res.newWhilePending = await form.getByRole("button", { name: "Назначить", exact: true }).getAttribute("aria-disabled");
  await p.screenshot({ path: `${OUT}/a2_pending_unknown.png`, fullPage: true });
  await p.getByRole("button", { name: "Проверить квитанцию", exact: true }).click();
  await p.waitForSelector(".aa-pending", { state: "detached", timeout: 20000 });
  res.afterReceipt = await msg(p).textContent();
  await p.getByRole("button", { name: "Показать", exact: true }).click(); await p.waitForTimeout(1000);
  const row = p.locator("tr", { hasText: ROLE });
  res.assignmentRow = (await row.innerText()).replace(/\s+/g, " ");
  await row.getByRole("button", { name: "Отозвать", exact: true }).click();
  await p.getByLabel("Причина").fill("Проверка UI C0056 завершена");
  await p.getByRole("button", { name: "Подтвердить отзыв", exact: true }).click();
  await p.waitForFunction(() => /Отзыв/.test(document.querySelector(".aa-msg")?.textContent || ""), null, { timeout: 20000 });
  res.revoked = await msg(p).textContent(); await p.waitForTimeout(1000);
  res.assignmentAfterRevoke = (await p.locator("tr", { hasText: ROLE }).innerText()).replace(/\s+/g, " ");
  await p.screenshot({ path: `${OUT}/a3_assignments_desktop.png`, fullPage: true });
  // Объяснение доступа.
  await p.click("#aa-tab-explain");
  await p.getByLabel("Право").fill("transport_dispatch_view"); await p.getByLabel("Код объекта").fill("1");
  await p.getByRole("button", { name: "Проверить", exact: true }).click();
  await p.waitForSelector(".aa-panel .aa-msg", { timeout: 20000 });
  res.explain = (await p.locator(".aa-panel .aa-msg").innerText()).replace(/\s+/g, " ");
  // Тестовая роль выключается.
  await p.click("#aa-tab-roles"); await p.locator("tr", { hasText: ROLE }).getByRole("button", { name: "Изменить", exact: true }).click();
  await p.getByLabel("Активна").uncheck(); await p.getByRole("button", { name: "Сохранить роль", exact: true }).click();
  await p.waitForFunction(() => /версия 2/.test(document.querySelector(".aa-msg")?.textContent || ""), null, { timeout: 20000 });
  res.roleFinal = await msg(p).textContent();
  // Mobile.
  const m = await page({ width: 390, height: 844 });
  await m.getByRole("button", { name: "Показать", exact: true }).click(); await m.waitForTimeout(1200);
  res.mobile = { overflow: await m.evaluate(() => document.documentElement.scrollWidth - innerWidth) };
  await m.locator(".help-hint-trigger").first().click();
  res.mobile.hintPosition = await m.locator(".help-hint-panel").evaluate(n => getComputedStyle(n).position);
  await m.screenshot({ path: `${OUT}/a4_mobile.png` });
  res.testObjects = { role: ROLE, group: GROUP };
  fs.writeFileSync(`${OUT}/../c0056_block2_result.json`, JSON.stringify(res, null, 1));
  console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
