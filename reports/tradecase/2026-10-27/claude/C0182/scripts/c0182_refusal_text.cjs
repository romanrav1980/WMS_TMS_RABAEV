// C-0182 focused UI test (no network): the plan and visit refusal texts for YARD_DOCK_BLOCKED and their fallbacks, from the real yardModel.ts.
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = "C:/projects/TMS/admin/wms_admin_frontend";
const ts = require(ROOT + "/node_modules/typescript");
const src = fs.readFileSync(ROOT + "/src/features/platform/workspaces/shift/yardModel.ts", "utf8");
const js = ts.transpileModule(src, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 } }).outputText;
const m = { exports: {} }; new Function("module", "exports", "require", js)(m, m.exports, () => ({}));
const { planRefusalText, refusalText } = m.exports;
const blocked = planRefusalText("YARD_DOCK_BLOCKED");
assert.ok(blocked.includes("неисправными") && blocked.includes("План или назначение не создано") && blocked.includes("Текущие визиты и планы не менялись"), blocked);
assert.strictEqual(refusalText("YARD_DOCK_BLOCKED"), blocked);  // the visit dock assignment uses the same explanation
assert.ok(planRefusalText("YARD_DOCK_PLAN_CONFLICT").includes("пересекающееся"));
assert.ok(planRefusalText("SOMETHING_NEW").includes("SOMETHING_NEW"));  // an unknown code stays visible, never a success
const out = { status: "PASS", YARD_DOCK_BLOCKED: blocked, unknown: planRefusalText("SOMETHING_NEW") };
fs.writeFileSync(path.join(__dirname, "..", "c0182-refusal-text.json"), JSON.stringify(out, null, 1));
console.log("PASS");
