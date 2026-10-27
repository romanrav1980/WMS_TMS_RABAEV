// C-0183 focused test (no network): yard visit and dock-plan refusal texts from the real yardModel.ts.
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = "C:/projects/TMS/admin/wms_admin_frontend";
const ts = require(ROOT + "/node_modules/typescript");
const js = ts.transpileModule(fs.readFileSync(ROOT + "/src/features/platform/workspaces/shift/yardModel.ts", "utf8"),
  { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const m = { exports: {} }; new Function("module", "exports", "require", js)(m, m.exports, () => ({}));
const { refusalText, planRefusalText } = m.exports;
const fallback = c => refusalText(c).startsWith("Сервер отклонил действие (");
const NEW = { YARD_CANCEL_REASON_REQUIRED: "причину отмены", YARD_DOCK_AMBIGUOUS: "повторяется в справочнике", YARD_REQUEST_INVALID: "не принял данные", YARD_INBOUND_UNSUPPORTED: "приёмки" };
const out = { status: "FAIL", texts: {} };
for (const [code, part] of Object.entries(NEW)) {
  for (const f of [refusalText, planRefusalText]) { const t = f(code); assert.ok(t.includes(part) && !fallback(code), `${code}: ${t}`); out.texts[code] = t; }
}
assert.ok(refusalText("YARD_DOCK_BLOCKED").includes("неисправными")); out.texts.YARD_DOCK_BLOCKED = refusalText("YARD_DOCK_BLOCKED");
for (const code of ["YARD_FUTURE_CODE", "YARD_RESULT_UNKNOWN", "YARD_PLAN_WINDOW_INVALID", "YARD_SUPPLY_BOUND"]) {
  assert.ok(fallback(code) && refusalText(code).includes(code), code);  // unknown/infra/read codes keep the visible fallback, never success
  out.texts[code] = refusalText(code);
}
out.status = "PASS";
fs.writeFileSync(path.join(__dirname, "..", "c0183-yard-refusals.json"), JSON.stringify(out, null, 1));
console.log("PASS", Object.keys(out.texts).length);
