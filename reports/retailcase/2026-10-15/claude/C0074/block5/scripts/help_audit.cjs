// C0074: аудит справки — у каждой кнопки/поля/объекта сцены рабочих мест есть подсказка (title или tooltip) и стабильный help_id.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const BASE = "http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html?workspace=";
const ROLES = ["director", "shift", "receiving", "storage", "dispatcher", "yard", "picker", "reach", "driver"];
const WH = { shift: "6558233", receiving: "", storage: "1", director: "", dispatcher: "", yard: "" };
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async () => {
  const b = await chromium.launch(); const res = {};
  for (const role of ROLES) {
    const p = await (await b.newContext({ viewport: { width: 1600, height: 1100 } })).newPage();
    await p.goto(BASE + role); await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass);
    await p.click("button[type=submit]"); await p.waitForTimeout(4000);
    if (WH[role]) { await p.locator(".rg-window input").first().fill(WH[role]); await p.waitForTimeout(4000); }
    // Гант: выбираем склад, чтобы проверить и его элементы.
    const gw = p.locator(".rg-planner .rg-window input[list]");
    if (await gw.count()) { await gw.first().fill(role === "shift" ? WH.shift : "6667491"); await p.waitForTimeout(3500); }
    res[role] = await p.evaluate(() => {
      const sel = "main button, main input, main select, main [role=button], main [role=tab], .ops-device button, .ops-device input, .ops button, .ops input, .ops select, .ops [role=button]";
      const els = [...new Set(document.querySelectorAll(sel))].filter(e => !e.closest(".kp-panel, .help-hint-pop") && e.offsetParent !== null || e.tagName === "g");
      const bad = [];
      for (const e of els) {
        // Строго: свой атрибут, либо ближайшая подпись <label> / группа кнопок [role=group|tablist] (help_id набора). Предки-дорожки не засчитываются.
        const near = e.closest("label, [role=group], [role=tablist], .help-action");
        const group = e.closest("[role=group], [role=tablist]");
        const helpId = e.getAttribute("data-help-id") || near?.getAttribute("data-help-id") || near?.querySelector?.("[data-help-id]")?.getAttribute("data-help-id") || group?.getAttribute("data-help-id");
        const desc = e.getAttribute("aria-describedby");
        const tip = e.getAttribute("title") || e.querySelector?.(":scope > title")?.textContent || (desc && document.getElementById(desc)?.textContent) || near?.getAttribute("title");
        if (!helpId || !tip) bad.push({ tag: e.tagName, text: (e.textContent || e.getAttribute("aria-label") || e.getAttribute("placeholder") || e.type || "").trim().slice(0, 40), helpId: helpId || null, tip: Boolean(tip) });
      }
      return { total: els.length, missing: bad };
    });
    await p.close();
  }
  fs.writeFileSync(`${OUT}/../help_audit_result.json`, JSON.stringify(res, null, 1));
  for (const [r, v] of Object.entries(res)) console.log(r, v.total, "missing", v.missing.length, JSON.stringify(v.missing.slice(0, 12)));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
