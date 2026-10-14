from pathlib import Path
import json,re
f=Path("db/migrations/2026-10-11_ni042_stack_stage");out={}
out[str(f/"005_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-210-case-stacking-stage'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Versioned WMS SKU stacking stage frozen on issued CASE line',sysdate,user,
'db/migrations/2026-10-11_ni042_stack_stage/apply.sql','db/migrations/2026-10-11_ni042_stack_stage/rollback.sql','APPLIED',
'Own CASE1107/wave461/BASE then TOP/native picks1+1, issued policy1 stays after future swapped SKU stage, omission preserves new stage, immutable direct update20863. CASE1108/wave462 TOP then BASE409 before first movement. Both native cleanup0/protected13520/20; six invalidated dependencies explicitly compiled.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@004_recompile.sql\n@@005_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=[x.replace("../2026-10-11_ni042_route_sequence/001_admission.sql","../2026-10-11_ni042_stack_stage/003_route.sql")for x in m["components"]]
m["startup_scripts"].append("../2026-10-11_ni042_stack_stage/001_schema.sql")
m["additional_scripts"].append("../2026-10-11_ni042_stack_stage/002_capture.sql")
m["required_columns"]["RRL_SKU_RECEIPT_POLICY"].append("STACK_STAGE")
m["required_columns"].setdefault("RRL_CASE_PICK_LINE",[]).extend(["STACK_STAGE","STACK_POLICY_VERSION"])
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni042_stack_stage_20261011.md"]="""# NI04.2: основание, середина, верх выданного места
210 APPLIED; [[nicora_ni042_stack_stage_design_20261011]]; [[nicora_ni042_route_sequence_20261011]].
Existing WMS SKU receiving-policy/card/version/audit extended STACK_STAGE BASE/MAIN/TOP, optional old-client input preserves current stage. Default MAIN preserves legacy behavior; no inference from ABC or weight threshold. Existing CASE line gets authoritative stage+source policy version at insert through metadata-only trigger, update immutable. Quantity triggers remain disabled; stock sole writer unchanged.
Existing native route guard validates nondecreasing stages along issued physical rank before first pick and again under CASE mutex, lower stage first at same point. Conflicting TOP before BASE refuses409; never sorts weights into backward route. Current SKU changes do not alter issued stage/source/rank. UI SKU stage selection plus TSD next-point stage, CASE reader returns captured fields.

Actual positive QC210F143F90631/secondSKU B, WARE35811577/revision311/CASE1107/wave461: source2+2, issued BASE/TOP/policy1, future policies swapped and old-client omission preserves new TOP, issued snapshot unchanged, direct stage rewrite20863. Two cells original ranks1→2, ahead refusal, native1+1/exact replay, close rollback, original return/release/tare0/wave deferred/count0/protected13520/20.
Negative QC210F4094872C8/WARE35993160/revision312/CASE1108/wave462: issued TOP then BASE; first pick409 CASE_STACK_ROUTE_CONFLICT/picked0 despite future corrected card. Initial cleanup tried tare cancellation before empty CASE cancellation and native correctly refused PHYSICALLY_UNUSED; repaired existing empty-return→tare-release→wave-defer→stock-count chain. Runnable fixture corrected. Two earlier pre-stock fixture attempts hit stale API schema and server restart readiness; no goods born. No independent review/physical loading stability claimed.

Six SKU-policy-dependent package bodies invalidated by additive DDL, explicitly recompiled (004_recompile.sql); final current INVALID/errors check required. Route layout groupedquery3a7dswf69g8xt .868ms/6 and nextstage4yd9v639cfy0t1.536ms/5: keep CASE-key index/200bound, fulfillment owner evaluate at load. Recovery preserves explicit configured/issued stages; rollback refuses with staged history, restore matching application source checkpoint before compatible SQL rollback.
"""
for path,line in [
("wiki/index.md","- [Этап укладки выданного CASE](database/nicora_ni042_stack_stage_20261011.md):210 versioned SKU BASE/MAIN/TOP frozen at issue; correct route picks, inverse route refused before stock; existing CASE owner."),
("wiki/log.md","2026-10-11:210 WMS SKU stacking-stage card/version/audit and frozen CASE line metadata/native stage-route guard applied. Actual1107 BASE→TOP1+1/replay/future policy preserved;1108 TOP→BASE409/zero pick. Native cleanup correct emptyCASE-before-tare ordering/protected13520/20. Six dependencies recompiled; aggregate .868/1.536ms retain CASE index/200bound."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:210 SKU stage BASE/MAIN/TOP and sourceversion frozen at CASE issue; original one-way route must fit foundation before uppergoods, conflict refused before stock instead of backwards route. Actual correct two-cell1+1/replay/issuedstage afterfuturechange and inverse409/cleanup. Master-data operator classifies physical foundation; engineering loadbearing/pilot not inferred.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI04.2").setdefault("implementedSlices",[]).append("210 versioned SKU BASE/MAIN/TOP setting and immutable issued CASE stage; native one-way stage compatibility/lower samepoint stage first; future settings do not rewrite issued cargo")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"210_stacking_stage.md")]="""# Qwen:210
Run scripts/ni042_stacking_stage_case.py, then --conflict dedicateddev. BASE1→TOP2 confirms1+1 at distinct cells; opposite TOP→BASE refuses before any stock. Captured stage/source policy1 stays after later swapped SKU policy; old client omission preserves configured stage, raw issued stage rewrite20863. Samepoint lower-stage order, unresolved shortage blocks; accepted SHORT_PICKED terminal. Default MAIN backward-compatible. Return each leaf original cell; empty CASE cancelled before held tare release, then wave deferred/native counts0/protected13520/20. Physical heavy/light classification assigned by responsible user; no weight threshold/physical pilot claim.
"""
print(json.dumps(out,ensure_ascii=True))
