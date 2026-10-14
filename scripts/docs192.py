from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni042_weight_decision")
out[str(f/"005_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-192-weight-tolerance-decision'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Explicit signed original order weight decision in existing CASE short approval root',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_decision/apply.sql','db/migrations/2026-10-11_ni042_weight_decision/rollback.sql','APPLIED',
'CASE1070 short20 exact9.6/10/15 percent frozen metadata/no false inventory/P20H9.6/SHORT_PICKED; rollback outbox+decision+H passed; concurrent identical result/stale409/immutable proof/current scopes. Pool return-aware waiver next.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@005_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));parts=m["components"];slot=parts.index("171_case_short_command.sql")
parts.remove("171_case_short_command.sql");parts.remove("../2026-10-11_ni042_order_weight_policy/002_preview.sql")
parts[slot:slot]=["../2026-10-11_ni042_weight_decision/003_read.sql","../2026-10-11_ni042_weight_decision/002_decision.sql","../2026-10-11_ni042_weight_decision/004_short_contract.sql"]
m["packages"].append("RRL_CASE_WEIGHT_DECISION");m["additional_scripts"].append("../2026-10-11_ni042_weight_decision/001_schema.sql")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_weight_decision_20261011.md"]="""# NI04.2: явное завершение CASE по допуску массы
192 APPLIED. [[retailcase_ni042_weight_decision_design_20261011]], [[retailcase_ni042_order_weight_policy_20261011]].
Existing CASE_SHORT_APPROVE accepts WEIGHT_TOLERANCE; no second stock command/writer. Current approver scope/permission, reason≥3, policy/content versions and SHA256 original order source preview required. Native current helper recompiles order SKU snapshot before and under sorted planned original customer order/all SKU rows/all related PT/plan anchors (200 rows/2000 PT). Same original planning locks block new-plan insert; PT locks block CASE pick/return and full pallet fact updates. Global CONFIG SHARE freezes current card. Whole source equality plus signed expected snapshot refuses changed source.
Existing native short flow releases only unused HARD and sets SHORT_PICKED/DONE; actual P/physical boxes/exact picked mass unchanged. Weight metadata stored on original short: policy version/pct/original requestedKG/current pickedKG/root decision operation FK. Guard rejects fabricated insert/update/delete proof, original metadata immutable; ordinary legacy decisions unchanged. Weight deviation skips false inventory discrepancy task.
Pure order preview includes CLOB SHA256 (verified live DBMS_CRYPTO CLOB overload); approver-only /shorts/{id}/weight-preview reads current same snapshot/scope. ARM button shows original/fact/pct, asks reason and saves original immutable body before sending; retry uses old saved body. No shortage/opening bypass on marked units.
Actual scripts/ni042_order_weight_decision_case.py QW192E51693DEC7/WARE35013523/revision265/wave431 CASE1070/short20/WEIGHT192.DECIDE:e51693dec7: stable NET9.6 original10/pct15, stale signature409, native prepare+execute and outer rollback restored pending short/H10/no outbox. Two concurrent same operation replies identical; final immutable metadata1/15/10/9.6, inventoryNULL, P20/H9.6/SHORT_PICKED. Direct proof rewrite20863; current native cleanup/original13520/20 unchanged. Original decision history retained ACCEPTED after physical CASE return.
Architecture original schemas growth rejected; decision DTO extracted into inventory contract with lightweight public contracts.py barrel and legacy schema import alias, no cycles/new debt. Baseline size allowance tightened1429→1425, architecture545/0/76PASS. RawJS syntax PASS. USER_ERRORS empty/all live objectsVALID after application.
Decision update b784kz2bh7hrv4.658ms/2, source8.605ms first read; retain PK/bounded order/PT closure. Inventory owner batch order-history aggregation/plan before pilot; no million-op claim.
Next193: current accepted deviation must affect original remaining demand only while related physical fulfillment remains valid; returned/cancelled CASE must reopen demand without deleting immutable approval. Until that integration no full NS36/NI04.2 closure claim. Over-plan12/lastbox exception remains separate.
"""
for path,line in [
("wiki/index.md","- [Явное завершение по допуску массы](database/retailcase_ni042_weight_decision_20261011.md):192 existing native short owner/exact9.6/10/signed approval/H release/rollback+replay; demand waiver next."),
("wiki/log.md","2026-10-11:192 APPLIED explicit CASE weight tolerance decision, signed original order/version/current planned PT locks; CASE1070/short20 actual9.6/10/15/no false inventory/P20H9.6/rollback outbox/concurrent replay/stale409/immutable history. DTO public contract extraction/size baseline tightened1425/architecture5450cycles76debt. Return-aware pool waiver next."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:192 explicit signed WEIGHT_TOLERANCE via existing CASE_SHORT_APPROVE/ARM, exact mass/P unchanged/unused HARD released/no false inventory. Actual1070/short20/rollback-outbox/concurrent saved replay passed. Original remaining-demand waiver/return reopening and lastbox exception remain next.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"192_weight_decision.md")]="""# Qwen:192
Run ni042_order_weight_decision_case.py dedicated dev. Independently test approval-only user/current warehouse/revoked role, signature/content/policy changes after preview, exact15% boundary and epsilon, reason missing, concurrent different/same IDs, native outer rollback including outbox/reserves/proof; original P unchanged. Marked intact box never split. ARM preview/reason/durable immutable retry/no auto close. Existing ACCEPT_SHORT/RESTORE unchanged. Returned CASE preserves historical immutable weight decision; original demand is still pending separate193, do not falsely accept full sprint. Review bounded200rows/2000PT sorted lock closure, statistics/batching plan.
"""
print(json.dumps(out,ensure_ascii=True))
