// C-0168: the receiving markup with its styles (FIXTURE, no scripts, no API): the factory pallet hint is visible and fits 1440/390.
const fs = require("fs"), path = require("path"), assert = require("assert");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const UI = "C:/projects/TMS/wiki-raw/wms_admin_ui_reference", OUT = path.join(__dirname, "..");
const res = { kind: "FIXTURE_MARKUP", checks: [] };
(async () => {
  const b = await chromium.launch();
  try {
    for (const w of [1440, 390]) {
      const p = await (await b.newContext({ viewport: { width: w, height: 900 } })).newPage();
      let html = fs.readFileSync(UI + "/receiving.html", "utf8").replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, "");
      html = html.replace(/<link\b[^>]*href="([^"]+\.css)[^"]*"[^>]*>/gi, (m, f) => fs.existsSync(UI + "/" + f) ? "<style>" + fs.readFileSync(UI + "/" + f, "utf8") + "</style>" : "");
      await p.setContent(html); await p.evaluate(() => document.body.classList.remove("auth-pending"));
      const hint = p.locator("#receiptFactoryHint");
      // the scan section is shown by the page script for a marked line; reveal its ancestors for the static check
      await p.evaluate(() => { document.getElementById("receiptMarking").hidden = false; });
      const why = await hint.evaluate(el => { const r = el.getBoundingClientRect(); return { w: r.width, h: r.height, text: el.innerText.slice(0, 60) }; });
      assert(why.w > 0 && why.h > 0 && /отсканируйте только её код/.test(await hint.innerText()), JSON.stringify(why));
      const box = await hint.evaluate(el => Math.round(el.getBoundingClientRect().right));
      const withHint = await p.evaluate(() => document.documentElement.scrollWidth);
      const parentRight = await hint.evaluate(el => Math.round(el.parentElement.getBoundingClientRect().right));
      const without = await p.evaluate(() => { const h = document.getElementById("receiptFactoryHint"); h.hidden = true; const v = document.documentElement.scrollWidth; h.hidden = false; return v; });
      assert(withHint <= without && box <= parentRight + 1, JSON.stringify({ withHint, without, box, parentRight }));
      res.checks.push({ width: w, name: "factory pallet hint present; does not widen the page", page_scroll_width_with: withHint, page_scroll_width_without: without, hint_right: box, container_right: parentRight });
      console.log("PASS", w, withHint, without, box, parentRight);
    }
    res.status = "PASS";
  } catch (e) { res.status = "FAIL"; res.error = String(e); console.error(e); }
  finally { await b.close(); }
  fs.writeFileSync(path.join(OUT, "c0168-ui.json"), JSON.stringify(res, null, 1)); process.exit(res.status === "PASS" ? 0 : 1);
})();
