from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni042_order_weight_policy")
out[str(f/"004_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-191-order-weight-policy'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Separate exact SKU order weight tolerance default15 and current original order SKU preview',sysdate,user,
'db/migrations/2026-10-11_ni042_order_weight_policy/apply.sql','db/migrations/2026-10-11_ni042_order_weight_policy/rollback.sql','APPLIED',
'CASE1069 original10/picked9.6 within15 outside2; default/current card history/version/stale409/invalid100.01422/old clients preserve2. Explicit completion/lastbox next; native original requested_base_quantity, not unallocated pool quantity.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@003_dependents.sql\n@@004_ledger.sql\n"
out[str(f/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-11-191-order-weight-policy","sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in f.glob("*.sql")},"recovery":"Additive default15 metadata; rollback refuses configured changes; no DB copy"},indent=2)
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));m["components"].append("../2026-10-11_ni042_order_weight_policy/002_preview.sql");m["packages"].append("RRL_ORDER_WEIGHT_READ");m["additional_scripts"].append("../2026-10-11_ni042_order_weight_policy/001_policy.sql")
if "RRL_SKU_RECEIPT_POLICY"in m.get("protected_columns",{}):m["protected_columns"]["RRL_SKU_RECEIPT_POLICY"].append("ORDER_WEIGHT_TOLERANCE_PCT")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_order_weight_policy_20261011.md"]="""# NI04.2: допуск массы исходного заказа
191 APPLIED. [[retailcase_ni042_order_weight_policy_design_20261011]], [[retailcase_ni042_scale_net_20261011]].
Existing RRL_SKU_RECEIPT_POLICY receives ORDER_WEIGHT_TOLERANCE_PCT default15/notnull/exact NUMBER5,2/check0..100. Existing versioned CONFIG X SKU save/log/card displays setting, Decimal binds; omission by old clients preserves current value. This is separate from legacy DEF_PERC (Form1.cs incoming quantity export deduction) and device resolution/QC gross tolerance.
Pure RRL_ORDER_WEIGHT_READ uses current CASE warehouse/permission, original order SKU rows bounded200, exact original requested_base_quantity and actual picked_quantity from existing pool reader. Current card pct/version, original order bounds/actual mass/currentcontent snapshot exposed READ ONLY /order-weight-preview and raw TSD. Preview does not complete or waive demand.
Own QW1913F055256ED/WARE24130130/revision264/wave430 CASE1069/source NET9.6 demand10/P20H10: original order10 and fact9.6 within15 bounds8.5..11.5; save2.00 -> outside2 bounds9.8..10.2, staleversion409/>100422, older client omitted value preserved2, restore15. SKU change journal saved. Native cleanup/original13520/20 unchanged.
Initial invalid DEFAULT15 syntax rejected before any DDL; corrected DEFAULT 15. Initial preview mistakenly read pool quantity (unallocated0 after HARD) and positive parser refused; corrected original requested_base_quantity. Failed owned fixtures6cb9f1a864/53423f7b69/7a4e0bafbc/d55d7a32f9 all native cleaned. Decimal15.0 representation author comparison corrected to exact Decimal; no data rounding.
Additive policy column invalidated five existing dependent bodies;003_dependents explicitly recompiled them with0errors. Native error/status verification after compile recorded in session. Architecture544/0/76 and JS syntax PASS; encoding passed following final check.
Preview53bjfk1wbz8j2 10.820ms/10: keep original-order≤200 and existing PK/planline lookup; inventory owner bulk aggregation/plan review before larger order history, no speculative index. Lastbox8/12 exception and explicit order deviation completion remain next; real hardware acceptance remains open.
"""
for path,line in [
("wiki/index.md","- [Допуск массы исходного заказа](database/retailcase_ni042_order_weight_policy_20261011.md):191 SKU default15/exact versioned setting/original10 vs picked9.6/current preview; explicit decision next."),
("wiki/log.md","2026-10-11:191 APPLIED separate order weight tolerance/card/history/current original SKU preview; CASE1069 within15/outside2/old-client preservation/stale409 passed. Corrected unallocated-vs-original quantity; five dependent bodies recompiled. Preview10.820ms/10 bounded200; inventory batching/plan owner."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:191 SKU order tolerance default15/exact0..100/card/version/history/current original orderSKU preview installed; 9.6/10 within15 outside2 confirmed. No automatic closure; explicit deviation and last-box exception next.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"191_order_weight_policy.md")]="""# Qwen:191
Run ni042_order_weight_policy_case.py dedicated dev. Inspect exact0/15/100/2.01 bounds, extra decimals rejected, stale versions/history, old client omission preserves current value, current WARE/cancelled rows/other SKU/case returns/previous picks included in original order preview. Confirm requested_base_quantity used (pool quantity after HARD may0), no auto order close or waived shortage, no DEF_PERC change. UI SKU save/TSD preview/current generation races. Native dependents VALID after ALTER. Review ≤200 rows/pool planline SQL batching before pilot.
"""
print(json.dumps(out,ensure_ascii=True))
