// C-0071/C-0070: (1) правка текста во время неизвестного исхода сохранения не стирается квитанцией старой команды;
// (2) после импорта wiki открывается созданный черновик; (3) вкладка «Оргобъекты»: создание неактивного тестового РЦ.
// Создаёт тестовую статью-черновик ui-c0056-probe (не публикуется) и неактивный объект DC UI.C0056.DC.*.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const login = async (p, url, ready) => { await p.goto(url); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass);
  await p.click("button[type=submit]"); await p.waitForSelector(ready, { timeout: 30000 }); await p.waitForTimeout(800); };
(async () => {
  const b = await chromium.launch(); const res = {};
  const p = await (await b.newContext({ viewport: { width: 1440, height: 1000 } })).newPage();
  const EDITOR = "http://127.0.0.1:3000/src/features/platform/knowledge-editor/preview/index.html";
  await login(p, EDITOR, "#ke-title");
  const exists = await p.locator(".ke-list li", { hasText: "ui-c0056-probe" }).count();
  if (exists) await p.locator(".ke-list li", { hasText: "ui-c0056-probe" }).getByRole("button", { name: "Открыть", exact: true }).click();
  else { await p.getByRole("button", { name: "Новая статья", exact: true }).click(); await p.getByLabel("Код статьи (article_id)").fill("ui-c0056-probe"); }
  await p.getByLabel("Заголовок").fill("Проверка C0056 (черновик, не публикуется)"); await p.getByLabel("Краткое описание").fill("Тест сохранения локального ввода.");
  await p.locator(".ke-editor textarea").first().fill("ВЕРСИЯ А — отправлена.");
  await p.getByLabel("Причина изменения").fill("C-0071 проверка");
  let dropped = false;
  await p.route("**/api/knowledge/commands", async route => { if (!dropped && route.request().method() === "POST") { dropped = true; await route.fetch(); return route.abort("connectionreset"); } return route.continue(); });
  await p.getByRole("button", { name: "Сохранить черновик", exact: true }).click(); await p.waitForSelector(".aa-pending", { timeout: 20000 });
  res.pending = (await p.locator(".aa-pending").first().innerText()).replace(/\s+/g, " ").slice(0, 120);
  await p.locator(".ke-editor textarea").first().fill("ВЕРСИЯ Б — набрана после обрыва."); await p.waitForTimeout(900);
  await p.getByRole("button", { name: "Проверить квитанцию", exact: true }).click();
  await p.waitForFunction(() => /сохранено/.test(document.querySelector(".aa-msg")?.textContent || ""), null, { timeout: 20000 });
  res.receipt = await p.locator(".aa-msg").first().textContent();
  res.localKeys = await p.evaluate(() => Object.keys(localStorage).filter(k => k.startsWith("retailcase.knowledge.draft")).map(k => [k.split(":").pop(), JSON.parse(localStorage.getItem(k)).draft.body]));
  await p.reload(); await login(p, EDITOR, "#ke-title");
  await p.locator(".ke-list li", { hasText: "ui-c0056-probe" }).getByRole("button", { name: "Открыть", exact: true }).click(); await p.waitForTimeout(1200);
  res.restoreOffered = await p.locator("[aria-label='Несохранённый текст']").count();
  if (res.restoreOffered) { await p.getByRole("button", { name: "Восстановить", exact: true }).click();
    res.restoredText = await p.locator(".ke-editor textarea").first().inputValue(); await p.getByRole("button", { name: "Удалить копию", exact: true }).count(); }
  res.serverBody = await p.evaluate(async () => (await fetch("http://127.0.0.1:8088/api/knowledge/articles/ui-c0056-probe", { headers: {} }).then(r => r.status)));
  // Импорт wiki открывает созданный черновик.
  await p.getByRole("tab", { name: "Из wiki", exact: true }).click(); await p.waitForSelector(".aa-list li", { timeout: 15000 });
  await p.locator(".aa-list li", { hasText: "ui-help-rules" }).getByRole("button", { name: "Предпросмотр", exact: true }).click(); await p.waitForSelector(".ke-preview", { timeout: 15000 });
  await p.getByLabel("Причина импорта").fill("C-0071: импорт открывает черновик");
  await p.getByRole("button", { name: "Создать черновик из wiki", exact: true }).click();
  await p.waitForFunction(() => /Импорт/.test(document.querySelector(".aa-msg")?.textContent || ""), null, { timeout: 20000 }); await p.waitForTimeout(1500);
  res.afterImport = { msg: await p.locator(".aa-msg").first().textContent(), modeArticles: await p.getByRole("tab", { name: "Статьи", exact: true }).getAttribute("aria-selected"),
    opened: await p.locator(".ke-editor-head h3").innerText().catch(() => "нет") };
  // Оргобъекты.
  const a = await (await b.newContext({ viewport: { width: 1440, height: 1000 } })).newPage();
  await login(a, "http://127.0.0.1:3000/src/features/platform/access-admin/preview/index.html", ".aa-meta b");
  await a.click("#aa-tab-objects"); await a.waitForTimeout(1500);
  res.objectsListDC = (await a.locator(".aa-panel").innerText()).replace(/\s+/g, " ").slice(0, 200);
  await a.locator(".aa-inline select").first().selectOption("WAREHOUSE"); await a.getByRole("button", { name: "Найти", exact: true }).first().click(); await a.waitForTimeout(1200);
  res.newWarehouseTitle = await a.getByRole("button", { name: "Новый объект", exact: true }).getAttribute("title");
  await a.locator(".aa-inline select").first().selectOption("DC"); await a.getByRole("button", { name: "Найти", exact: true }).first().click(); await a.waitForTimeout(800);
  await a.getByRole("button", { name: "Новый объект", exact: true }).click();
  const id = "UI.C0056.DC." + Date.now().toString(36);
  await a.getByLabel("Код", { exact: true }).fill(id); await a.getByLabel("Название").fill("Проверка UI C0056 (неактивный РЦ)"); await a.getByLabel("Активен").uncheck();
  await a.getByRole("button", { name: "Сохранить объект", exact: true }).click();
  await a.waitForFunction(() => /Объект/.test(document.querySelector(".aa-msg")?.textContent || ""), null, { timeout: 20000 });
  res.objectSaved = await a.locator(".aa-msg").first().textContent(); res.testObject = id;
  await a.screenshot({ path: `${OUT}/k6_objects.png`, fullPage: true });
  fs.writeFileSync(`${OUT}/../c0071_fixes_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
