// C0056 блок 3: KnowledgeEditorPage на реальном /api/knowledge/* (dev preview до интеграции в App).
// Создаёт и публикует две пользовательские статьи из docs/help/authoring (access-admin, knowledge-editor);
// проверяет восстановление локального черновика после перезагрузки; импортирует разрешённый источник wiki в ЧЕРНОВИК (без публикации).
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const URL0 = "http://127.0.0.1:3000/src/features/platform/knowledge-editor/preview/index.html";
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const md = id => {
  const text = fs.readFileSync(`C:/projects/TMS/docs/help/authoring/${id}.md`, "utf8");
  const [, front, body] = text.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  const get = k => (front.match(new RegExp("^" + k + ":\\s*(.*)$", "m")) || [, ""])[1].trim();
  const list = k => get(k).replace(/^\[|\]$/g, "").split(",").map(x => x.trim()).filter(Boolean);
  return { id, title: get("title"), summary: get("summary"), body: body.trim(), related: list("related"), sources: list("sources"), perms: list("required_permissions") };
};
const msg = p => p.locator(".aa-msg").first();

(async () => {
  const b = await chromium.launch(); const res = { posts: [], articles: {} };
  const ctx = await b.newContext({ viewport: { width: 1440, height: 1000 } });
  const login = async (p) => {
    await p.goto(URL0); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass);
    await p.click("button[type=submit]"); await p.waitForSelector("#ke-title", { timeout: 30000 }); await p.waitForTimeout(800);
  };
  const p = await ctx.newPage();
  p.on("request", r => { if (r.method() !== "GET" && r.url().includes("/api/")) res.posts.push(r.method() + " " + r.url().replace(/^https?:\/\/[^/]+/, "")); });
  await login(p);
  res.helpIds = await p.$$eval("[data-help-id]", n => n.length);
  for (const id of ["access-admin", "knowledge-editor"]) {
    const a = md(id);
    // Сначала связанные статьи должны существовать: knowledge-editor ссылается на access-admin, публикуемую первой.
    const exists = await p.locator(".ke-list li", { hasText: id }).count();
    if (exists) await p.locator(".ke-list li", { hasText: id }).getByRole("button", { name: "Открыть", exact: true }).click();
    else await p.getByRole("button", { name: "Новая статья", exact: true }).click();
    await p.waitForSelector(".ke-editor", { timeout: 15000 });
    if (!exists) await p.getByLabel("Код статьи (article_id)").fill(a.id);
    await p.getByLabel("Заголовок").fill(a.title); await p.getByLabel("Краткое описание").fill(a.summary);
    await p.locator(".ke-editor textarea").first().fill(a.body);
    await p.getByLabel("Связанные статьи (article_id через запятую)").fill(a.related.join(", "));
    await p.locator(".ke-editor textarea").nth(1).fill(a.sources.join("\n"));
    await p.getByLabel("Права чтения (через запятую, пусто — всем вошедшим)").fill(a.perms.join(", "));
    await p.getByLabel("Причина изменения").fill("C0056: пользовательская инструкция нового экрана");
    await p.getByRole("tab", { name: "Как увидит читатель", exact: true }).click();
    res.articles[id] = { previewRelated: (await p.locator(".ke-preview ul").innerText()).replace(/\s+/g, " ") };
    if (id === "access-admin") await p.locator(".ke-editor").screenshot({ path: `${OUT}/k1_preview.png` });
    await p.getByRole("tab", { name: "Текст", exact: true }).click();
    await p.getByRole("button", { name: "Сохранить черновик", exact: true }).click();
    await p.waitForFunction(i => (document.querySelector(".aa-msg")?.textContent || "").includes("Статья " + i), id, { timeout: 20000 });
    res.articles[id].saved = await msg(p).textContent(); await p.waitForTimeout(1200);
    await p.getByLabel("Причина публикации/архива").fill("C0056: публикация инструкции");
    await p.getByRole("button", { name: "Опубликовать", exact: true }).click();
    await p.waitForFunction(i => (document.querySelector(".aa-msg")?.textContent || "").includes("Публикация " + i), id, { timeout: 20000 });
    res.articles[id].published = await msg(p).textContent(); await p.waitForTimeout(1000);
  }
  // История и «Подробнее» → справка с опубликованной статьёй.
  await p.getByRole("tab", { name: "История", exact: true }).click(); await p.waitForSelector(".ke-editor .aa-table", { timeout: 15000 });
  res.history = (await p.locator(".ke-editor .aa-table tbody").innerText()).replace(/\s+/g, " ").slice(0, 300);
  await p.getByRole("tab", { name: "Текст", exact: true }).click();
  await p.locator(".help-hint-trigger").first().click(); await p.getByRole("button", { name: "Подробнее", exact: true }).click();
  await p.waitForSelector("dialog.knowledge-panel[open] article h3", { timeout: 15000 });
  res.helpOpened = await p.locator("dialog.knowledge-panel article h3").textContent();
  await p.keyboard.press("Escape"); await p.waitForTimeout(300);
  // Локальный черновик переживает перезагрузку.
  await p.locator(".ke-editor textarea").first().fill(md("knowledge-editor").body + "\n\nЛОКАЛЬНАЯ ПРАВКА C0056");
  await p.waitForTimeout(900);
  await p.reload(); await login(p);
  await p.locator(".ke-list li", { hasText: "knowledge-editor" }).getByRole("button", { name: "Открыть", exact: true }).click();
  await p.waitForSelector("[aria-label='Несохранённый текст']", { timeout: 15000 });
  res.restoreOffered = (await p.locator("[aria-label='Несохранённый текст']").innerText()).replace(/\s+/g, " ");
  await p.screenshot({ path: `${OUT}/k2_restore_after_reload.png`, fullPage: true });
  await p.getByRole("button", { name: "Восстановить", exact: true }).click();
  res.restoredHasEdit = (await p.locator(".ke-editor textarea").first().inputValue()).includes("ЛОКАЛЬНАЯ ПРАВКА C0056");
  res.publishWhileUnsaved = await p.getByRole("button", { name: "Опубликовать", exact: true }).getAttribute("title");
  // Убираем локальную правку: перечитать статью и удалить копию.
  await p.reload(); await login(p);
  await p.locator(".ke-list li", { hasText: "knowledge-editor" }).getByRole("button", { name: "Открыть", exact: true }).click();
  await p.waitForSelector("[aria-label='Несохранённый текст']", { timeout: 15000 });
  await p.getByRole("button", { name: "Удалить копию", exact: true }).click();
  res.copyRemoved = await p.locator("[aria-label='Несохранённый текст']").count() === 0;
  // Из wiki: предпросмотр → черновик.
  await p.getByRole("tab", { name: "Из wiki", exact: true }).click(); await p.waitForSelector(".aa-list li", { timeout: 15000 });
  await p.locator(".aa-list li", { hasText: "ui-help-rules" }).getByRole("button", { name: "Предпросмотр", exact: true }).click();
  await p.waitForSelector(".ke-preview", { timeout: 15000 });
  res.wikiTarget = (await p.locator(".aa-form p").first().innerText()).replace(/\s+/g, " ");
  await p.getByLabel("Причина импорта").fill("C0056: проверка импорта из wiki (черновик, без публикации)");
  await p.screenshot({ path: `${OUT}/k3_wiki_preview.png`, fullPage: true });
  await p.getByRole("button", { name: "Создать черновик из wiki", exact: true }).click();
  await p.waitForFunction(() => /Импорт/.test(document.querySelector(".aa-msg")?.textContent || ""), null, { timeout: 20000 });
  res.wikiImport = await msg(p).textContent();
  await p.getByRole("tab", { name: "Статьи", exact: true }).click(); await p.waitForTimeout(1200);
  res.wikiDraftInList = (await p.locator(".ke-list li", { hasText: "ui-help-rules" }).innerText().catch(() => "нет")).replace(/\s+/g, " ");
  // Mobile.
  const m = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage(); await login(m);
  await m.locator(".ke-list li", { hasText: "access-admin" }).getByRole("button", { name: "Открыть", exact: true }).click(); await m.waitForTimeout(1200);
  res.mobile = { overflow: await m.evaluate(() => document.documentElement.scrollWidth - innerWidth) };
  await m.screenshot({ path: `${OUT}/k4_mobile.png` });
  fs.writeFileSync(`${OUT}/../c0056_block3_result.json`, JSON.stringify(res, null, 1));
  console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
