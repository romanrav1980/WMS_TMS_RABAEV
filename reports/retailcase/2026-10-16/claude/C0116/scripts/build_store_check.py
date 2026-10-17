# Собирает store_manual_weight_check.cjs: функция setup (фикстуры store-app API) берётся из проверки Codex
# reports/retailcase/2026-10-15/store-ui-claude-review/ux-final-help-recovery.cjs без изменений логики,
# плюс вес в фикстуре акта и проверки C0116.
from pathlib import Path

here = Path(__file__).parent
src = Path("C:/projects/TMS/reports/retailcase/2026-10-15/store-ui-claude-review/ux-final-help-recovery.cjs").read_text(encoding="utf-8")
setup = src[: src.index("(async()=>{")]
setup = setup.replace("require('../../../../admin/wms_admin_frontend/node_modules/playwright')", "require('C:/projects/TMS/admin/wms_admin_frontend/node_modules/playwright')")
setup = setup.replace("require('../../../../terminal/wms_terminal_web/node_modules/@zxing/library')", "require('C:/projects/TMS/terminal/wms_terminal_web/node_modules/@zxing/library')")
old = "const receipt=op=>({operation_id:op,"
assert old in setup
setup = setup.replace(old, (
    "const weightOf=body=>body&&body.manual_weight_kg?{capture_key:null,device_id:null,device_policy_version:null,measurement_origin:'MANUAL_CONFIRMED',"
    "recorded_by:'receiver',shipping_gross_kg:'12',observed_gross_kg:body.manual_weight_kg,tolerance_kg:'0.5',delta_kg:'0.45',in_tolerance:1,act_confirmed:0,photos:[]}"
    ":body&&body.scale_capture_key?{capture_key:body.scale_capture_key,device_id:'SCALE-12',device_policy_version:1,measurement_origin:'SCALE_CAPTURE',recorded_by:'receiver',"
    "shipping_gross_kg:'12',observed_gross_kg:'12',tolerance_kg:'0.5',delta_kg:'0',in_tolerance:1,act_confirmed:0,photos:[]}:undefined;\n"
    "let lastBody=null;\nconst receipt=op=>({weight:weightOf(lastBody),operation_id:op,"))
old2 = "posts.push(req.postData());"
assert old2 in setup
setup = setup.replace(old2, "posts.push(req.postData());lastBody=JSON.parse(req.postData());")
main = (here / "store_checks_main.cjs.part").read_text(encoding="utf-8")
(here / "store_manual_weight_check.cjs").write_text(setup + main, encoding="utf-8")
print("built")
