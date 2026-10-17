// C-0090: вход водителя не наследует admin-сессию родительского окна. В сессии admin вводятся заведомо неверные учётные
// данные водителя (несуществующий пользователь) — ожидается отказ сервера; проверяется, что запросы /api/driver идут с
// пользователем водителя, а не admin, и без cookie. Пароль admin не печатается.
const fs = require("fs");
const { chromium } = require("C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright");
const OUT = process.argv[2];
const pass = fs.readFileSync("C:/projects/TMS/AGENTS.md", "utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
(async () => {
  const b = await chromium.launch(); const res = { driverRequests: [] };
  const p = await (await b.newContext({ viewport: { width: 390, height: 844 } })).newPage();
  p.on("request", r => { if (!r.url().includes("/api/driver")) return; const h = r.headers();
    const user = h.authorization ? Buffer.from(h.authorization.replace(/^Basic /, ""), "base64").toString().split(":")[0] : null;
    res.driverRequests.push({ path: new URL(r.url()).pathname, user, cookie: Boolean(h.cookie) }); });
  p.on("response", r => { if (r.url().includes("/api/driver")) res.driverStatus = r.status(); });
  await p.goto("http://127.0.0.1:3000/src/features/platform/workspaces/preview/index.html?workspace=driver");
  await p.fill("input[autocomplete=username]", "admin"); await p.fill("input[type=password]", pass); await p.click("button[type=submit]");
  await p.waitForSelector(".ops-device input[type=number]", { timeout: 30000 });
  const dev = p.locator(".ops-device");
  await dev.locator("input[type=number]").fill("1"); await dev.locator("input[autocomplete=username]").fill("no_such_driver_c0074");
  await dev.locator("input[type=password]").fill("wrong-password-c0074"); await dev.getByRole("button", { name: "Войти" }).click();
  await p.waitForTimeout(3000);
  res.screen = (await dev.innerText()).replace(/\s+/g, " ").slice(0, 300);
  res.inheritedAdmin = res.driverRequests.some(r => r.user === "admin");
  await p.screenshot({ path: `${OUT}/d1_driver_identity.png` });
  fs.writeFileSync(`${OUT}/../driver_identity_result.json`, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1)); await b.close();
})().catch(e => { console.error(e); process.exit(1); });
