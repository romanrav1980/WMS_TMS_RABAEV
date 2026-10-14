from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni042_weight_box_choice")
out[str(f/"006_context.sql")]="create context RRL_WEIGHT_CHOICE_CTX using RRL_WEIGHT_BOX_CHOICE_API;\n"
out[str(f/"007_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-195-approved-weight-box-choice'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Immutable approval-only final whole box choice inside existing business metadata owner',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_box_choice/apply.sql','db/migrations/2026-10-11_ni042_weight_box_choice/rollback.sql','APPLIED',
'Own QW1952E694BA0DE actual8/12 vs original10/default15/no split; approval-only actor/source signature/rawGS1/replay/conflicts/active unique/cancel history/current active status/P20H0 unchanged; no plan or stock effect; existing native planner use next.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@007_ledger.sql\n"
out[str(f/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-11-195-approved-weight-box-choice","before_reader_sha256":hashlib.sha256((f/"000_before_reader.sql").read_bytes()).hexdigest(),"current_sql_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in f.glob("*.sql")},"recovery":"Affected original reader saved; immutable choice archive rollback blocked when history exists; forward repair/no database copy"},indent=2)
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=[x.replace("../2026-10-11_ni042_weight_box_planning/002_options.sql","../2026-10-11_ni042_weight_box_choice/003_reader.sql")for x in m["components"]]
m["components"].append("../2026-10-11_ni042_weight_box_choice/005_recompile_api.sql");m["packages"].extend(["RRL_WEIGHT_BOX_CHOICE_API","RRL_PICK_PLAN_ADMISSION"])
m["startup_scripts"].append("../2026-10-11_ni042_weight_box_choice/001_schema.sql")
m["additional_scripts"].extend(["../2026-10-11_ni042_weight_box_choice/006_context.sql","../2026-10-11_ni042_weight_box_choice/004_guard.sql"])
cols=m["required_columns"]
cols["RRL_SKU_RECEIPT_POLICY"]=["POLICY_VERSION","MARKING_REQUIRED","SERIALIZED_WEIGHT_BOXES","ORDER_WEIGHT_TOLERANCE_PCT"]
for name,new in {
"RRL_CASE_PICK_SHORT":["WEIGHT_POLICY_VERSION","WEIGHT_TOLERANCE_PCT","WEIGHT_ORDER_REQUESTED_KG","WEIGHT_ORDER_PICKED_KG","WEIGHT_DECISION_OPERATION"],
"RRL_WH_SCALE_DEVICE":["DEVICE_ID","WARE_ID","POST_CELL","SENDER_ID","POLICY_VERSION","ACTIVE_FLAG","DEVICE_MODE","MEASUREMENT_BASIS","CAPACITY_KG","RESOLUTION_KG","CALIBRATION_REF","CALIBRATED_UNTIL"],
"RRL_WH_SCALE_CAPTURE":["CAPTURE_KEY","CASE_PICK_TASK_ID","CASE_PICK_LINE_ID","CASE_CONTENT_VERSION","WEIGHT_KG","MEASUREMENT_BASIS","SOURCE_SHA256","SOURCE_JSON","RESULT_JSON"],
"RRL_WH_SCALE_USE":["CAPTURE_KEY","STOCK_OPERATION_ID","CASE_PICK_TASK_ID","CASE_PICK_LINE_ID","ACTOR"],
"RRL_PICK_WEIGHT_CHOICE":["CHOICE_ID","CUSTOMER_ORDER_ROW_ID","WARE_ID","ARTICLE","PHYSICAL_UNIT_KEY","SOURCE_UID","SOURCE_CELL","STOCK_VERSION","NET_WEIGHT_KG","POLICY_VERSION","CHOICE_MODE","STATUS","SOURCE_SIGNATURE","SOURCE_JSON","REQUEST_JSON","RESULT_JSON","PICK_PLAN_ID","PICK_PLAN_LINE_ID","APPROVED_BY"]}.items():
 cols.setdefault(name,[])
 for col in new:
  if col not in cols[name]:cols[name].append(col)
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_weight_box_choice_20261011.md"]="""# NI04.2: согласование последней целой коробки
195 APPLIED. [[retailcase_ni042_weight_box_choice_design_20261011]], [[retailcase_ni042_weight_box_planning_20261011]].
Additive immutable RRL_PICK_WEIGHT_CHOICE captures original order row/warehouse/SKU/physical key/UID/cell/stockversion/exact net/frozen original order+remaining/pct+version/mode/reason/actor/raw request/full signed original source/result. Unique active original-row and physical-box sparse indexes prevent double intent; no P/H/stock writer/plan yet.
Native current approval-only rights and warehouse separated from pick-plan creation via restricted optional reader permission. Exact source signature/current AVAILABLE unit/measurements/rawGS1 decoded same identity and exact net required; WITHIN_TOLERANCE only inside default/current pct; LAST_WHOLE_BOX explicitly outside with reason, card default15 and scale precision unchanged. Existing CASE business metadata owner CONFIG X +WAREHOUSE.METADATA row anchor; no general warehouse-config permission granted. Trusted own TX/id/actor/phase context guard blocks arbitrary insert/edit/delete; cancellation retains original archive. Same choice+actor/request replay returns original receipt; changed content20873, active duplicate409. Current active_choice read separate from original saved receipt.
Raw customer-order panel supports approval-only user, physical barcode/reason form, explicit exception caption, original durable choice body/retry per API/user/row/unknown-outcome marker; known first refusal may clear new draft, unresolved old outcome retains. Active choice/cancel display; source metadata safe textContent. No physical fulfillment implied by approved intent.
Own scripts/ni042_weight_box_choice_case.py QW1952E694BA0DE/WARE23041611/revision272: actual8/12/original10/P20H0; QA1952e694ba0de has only case_pick_short_approve, no pick_plan_create. Planner preview403/approval preview200, choice8 LAST_WHOLE_BOX/source/GS1/default15 accepted, exact replay, changed reason409, active duplicate409, wrong label/stale source/WITHIN mode outsidewindow409, direct source overwrite20863. Current active choice8 visible, cancellation/retry original source preserved/activeNone/P-H unchanged. Native countcleanup/original13520/20; actor retired.
First65f9646801 fixture found lower-case physical SHA key DTO regex; now accepts exact registry hex in either case without rewriting. Second8f669a9bb4 wrongly used warehouse configuration owner (its whitelist excludes business approval); third e0038f3fc5 showed metadata owner deliberately grants no stock context. Corrected to existing business metadata transaction and own trusted namespace/held CONFIG X+metadata row anchor, no whitelist expansion. All three P/H cleaned natively and own actors retired via retire195_failed_actors.py. Later989c1813c7 positive passed before active-status addition;2e final passed after.
Native9stmts0errors/USER_ERRORS empty/allobjectsVALID; architecture548/0cycles/76debt and newJS syntax PASS; encoding check after final write. Approvalgyxdwk1r0v22915.904ms/18, insertb6f2wmz8f16qc15.287ms/4, active-readb7u3p5psgvc1a5.756ms/5, cancellation4.698ms/4: retain primary/sparse active indexes/rare short metadata fence; inventory owner bounded batch/plan review at high history. No production load/hardware/legalACK claim.
Current runtime required_columns now mirrors179..195 policy/physical/scale/use/decision fields; corrected earlier protected_columns key assumption without changing database. Source bundle generation only, not apply against ACTIVE.
Next196 consume choice within existing native plan/SOFT transaction/current source;197 HARD pin exact physical key;198 fulfilled/cancelled demand and lastbox8/12 end-to-end. NI04.2 remains open.
"""
for path,line in [
("wiki/index.md","- [Согласование последней целой коробки](database/retailcase_ni042_weight_box_choice_20261011.md):195 approval-only exact8-vs10/default15 unchanged/immutable source/replay/cancel/no P-H; existing plan use next."),
("wiki/log.md","2026-10-11:195 APPLIED immutable final whole-box choice/current approval-only warehouse/source/GS1/default15/no split. Own2e694ba0de8-vs10/replay/refusals/active unique/immutable/cancel/current status/no P-H passed; correct business metadata owner reused without stock/config-right grants. Three failed own actors retired. Required columns179..195 mirrored; nativeVALID/architecture5480cycles76debt/JS. Approval15.904ms18 bounded rare fence; inventory plan owner."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:195 current signed whole box8-vs10 explicit LAST_WHOLE_BOX approval archive/source/roles/active uniqueness/replay/cancel/UI delivered; no stock or plan effect.196 old native plan/SOFT consumption,197 exact HARD unit,198 fulfilled/returned demand next.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"195_whole_box_choice.md")]="""# Qwen:195
Run ni042_weight_box_choice_case.py dedicated dev. Approval-only actor distinct planner right/currentWARE; boxed8/12 original10/default15 unchanged/noSplit. Native source signature/version/physical label identity+net/measurements required, mode outsidewindow explicit reason. Idempotent exact request/actor, changed reuse conflict, unique active perrow andunit, metadata-only no P/H/plan. Direct insert/edit/delete refuse, cancel original archive/current active status, long1000-character Unicode reason. Browser durable unknown-body retry/auth peruser/source generation races/activecancel. Existing business metadata namespace+CONFIG X+metadata anchor (no stock context) must remain. Original receipt vs current status separated. Do not claim actual plan/HARD until196/197. Review indexed bounded native source/rare fence timings.
"""
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for item in m.get("sprints",[]):
 if item.get("id",item.get("code"))=="NI04.2":
  slices=item.setdefault("implementedSlices",[])
  for value in [str(n)for n in range(185,196)]:
   if value not in slices:slices.append(value)
out[str(p)]=json.dumps(m,ensure_ascii=True,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
