const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync("wiki-raw/wms_admin_ui_reference/warehouse-task-recovery.js", "utf8");
const saved = new Map();
const storage = new Proxy({
  getItem: key => saved.get(key) ?? null,
  setItem: (key, value) => { saved.set(key, value); },
  removeItem: key => saved.delete(key),
}, {ownKeys: () => [...saved.keys()],
    getOwnPropertyDescriptor: () => ({enumerable: true, configurable: true})});
let retry;
const panel = {setAttribute: () => {}, querySelector: kind => kind === "span" ? {} :
  {addEventListener: (_, callback) => { retry = callback; }}};
function load(fetcher) {
  const window = {wmsAdminAuth: {state: {apiBase: "dev", user: {username: "operator"}}},
                  dispatchEvent: () => {}};
  const document = {getElementById: () => null, createElement: () => panel,
                    querySelector: () => ({prepend: () => {}})};
  vm.runInNewContext(source, {window, document, localStorage: storage,
    crypto: {randomUUID: () => "same-id"}, CustomEvent: class {}, console});
  window.warehouseTaskRecovery.init(fetcher);
  return window.warehouseTaskRecovery;
}
(async () => {
  let calls = [];
  let lost = true;
  const fetcher = async (_, options) => {
    calls.push(options.body);
    if (lost) { lost = false; throw new Error("response lost after commit"); }
    return {result: {status: "DONE", quantity: "9007199254740993.000000001"}};
  };
  const body = {fact_qty: "9007199254740993.000000001", scanned_pallet: "internal-01"};
  await assert.rejects(load(fetcher).complete(17, body), /response lost/);
  assert.equal(saved.size, 1);
  load(fetcher); // A reloaded page restores the original body and operation id.
  await retry();
  assert.equal(calls.length, 2);
  assert.equal(calls[0], calls[1]);
  assert.equal(JSON.parse(calls[0]).fact_qty, body.fact_qty);
  assert.equal(saved.size, 0);
  await assert.rejects(load(async () => { throw Object.assign(new Error("uncertain"),
    {status: 503, code: "RESULT_UNCERTAIN"}); }).complete(18, body), /uncertain/);
  assert.equal(saved.size, 1);
  saved.clear();
  await assert.rejects(load(async () => { throw Object.assign(new Error("bad scan"),
    {status: 409, code: "STOCK_RULE_REJECTED", oracleCode: 20886}); }).complete(19, body), /bad scan/);
  assert.equal(saved.size, 0);
  console.log("PASS: exact durable replay after reload; uncertain result retained; proven rejection editable");
})().catch(error => { console.error(error); process.exitCode = 1; });
