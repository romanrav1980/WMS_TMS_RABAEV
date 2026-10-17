// C0116: экран погрузки — группа «Вес и размеры места — вводит пользователь», подсказки, help_id и ссылки справки.
// Только загрузка страницы и чтение DOM; команды погрузки не отправляются.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = path.join(__dirname, "..", "screenshots");
const URL0 = "http://127.0.0.1:8088/wms-admin/transport-loading.html";
(async () => {
  const b = await chromium.launch(); const res = { writes: [] };
  for (const [w, name] of [[390, "l1_loading_390.png"], [1440, "l2_loading_desktop.png"]]) {
    const p = await (await b.newContext({ viewport: { width: w, height: 1000 } })).newPage();
    p.on("request", r => { if (r.method() !== "GET" && r.url().includes("/api/")) res.writes.push(r.method() + " " + r.url()); });
    await p.goto(URL0); await p.waitForSelector("#loadGross", { state: "attached" });
    res.fields = await p.evaluate(() => ["loadGross", "loadWidth", "loadDepth", "loadHeight", "loadConfirm"].map(id => {
      const e = document.getElementById(id); return { id, title: !!e.title, helpId: e.dataset.helpId }; }));
    res.links = await p.evaluate(() => [...document.querySelectorAll(".loading-manual-measure a, a[data-help-id='loading.retry.help']")].map(a => a.getAttribute("href")));
    res.legend = await p.locator(".loading-manual-measure legend").innerText();
    const box = await p.locator(".loading-manual-measure").first(); await box.scrollIntoViewIfNeeded().catch(() => {});
    res["overflow" + w] = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    await p.screenshot({ path: path.join(OUT, name), fullPage: true });
  }
  assert(res.fields.every(f => f.title && f.helpId)); assert.deepEqual(res.writes, []);
  for (const href of res.links) { const r = await fetch("http://127.0.0.1:8088" + href.split("#")[0]); assert.equal(r.status, 200); }
  res.status = "PASS";
  fs.writeFileSync(path.join(__dirname, "..", "loading_help_result.json"), JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
