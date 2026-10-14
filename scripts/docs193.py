from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_weight_demand")
out[str(f/"003_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-193-weight-deviation-demand'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Current cancellation-aware accepted weight deviation in original pool demand math',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_demand/apply.sql','db/migrations/2026-10-11_ni042_weight_demand/rollback.sql','APPLIED',
'CASE1071 short21 original10/actual9.6/H9.6/accepted.4/current demand0; native CASE return demand10/waiver0, immutable approval retained. No stock writes/new allocator. Quality545/0/76/24/bothTS PASS.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@003_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));a="../2026-10-11_ni033_line_demand/001_pool.sql";assert a in m["components"];i=m["components"].index(a)
m["components"][i:i+1]=["../2026-10-11_ni042_weight_demand/001_waiver.sql","../2026-10-11_ni042_weight_demand/002_pool.sql"];m["packages"].append("RRL_WEIGHT_DEVIATION_READ")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_weight_demand_20261011.md"]="""# NI04.2: потребность после принятого отклонения
193 APPLIED. [[retailcase_ni042_weight_demand_design_20261011]], [[retailcase_ni042_weight_decision_20261011]].
Pure RRL_WEIGHT_DEVIATION_READ plugs original pool equation: original-HARD-nonoverlappingpicked-current accepted deviation. No new allocator or stock writer. Fast current indexed accepted-short lookup returns0 for ordinary rows. Current SHORT_PICKED/PTDONE/CASEnotcancelled/accepted immutable decision/rootOPAPPLIED required. Whole current order SKU original requestedKG equals frozen source; current actual all related PT stays inside frozen pct. Own-line waiver capped by original own requestedKG minus current actual. Config updates do not retroactively change accepted commercial agreement; source/return changes invalidate.
Original reader exposes accepted_weight_deviation_quantity and explicit changed quantity_semantics. original requested_base_quantity remains untouched. Existing planner174 uses pool output; separate new-order status/transport allocator not introduced.
Own scripts/ni042_order_weight_demand_case.py QW19384429EF381/WARE28667806/revision266/wave432 CASE1071/short21: original10/currentpicked9.6/H9.6/accepted.4/remaining0. Existing192 signedapproval/outer rollback includingoutbox/concurrent sameOP/stale signature409/immutable proof still passed. Native CASE return removes current waiver to0 and reopens original10, immutable approval still ACCEPTED; native countcleanup/original13520/20 unchanged.
Functional iteration found existing inventory/contracts.py had been accidentally overwritten by192 lightweight barrel creation. No new193 fixture began until restored passive reservation DTOs from HEAD schemas (matching149 extraction script); retained separate new CASE DTO export, compatibility aliases unchanged. See [[../incidents/retailcase_inventory_contract_overwrite_20261011]]. Full app OpenAPI200 contains all3 reservation DTOs/new approver preview; quality545files/0cycles/76debt/24tests/bothTS PASS after repair.
SQL accepted decisions7t3fgdx378m0d17.851ms/2 cold; fast COUNT8yw128juu9rcy1.392ms/12. Retain current indexed PK/planline joins and bounded200rows/2000PT/200decisions; inventory owner batch totals/plan review if many historical decisions, no speculative index/load claim. Realhardware/lastbox8or12 exception/whole variable box plan adaptation still open.
"""
out["wiki/incidents/retailcase_inventory_contract_overwrite_20261011.md"]="""# Перезапись публичных DTO inventory при192
During extraction of new CasePickShortDecisionRequest, inventory/contracts.py was mistakenly treated as absent and replaced with a4-line barrel, removing existing StockReservationCreate/Promote/StatusRequest. Architecture graph check did not detect deleted exports;193 import immediately failed before any fixture/stock operation. API reload could temporarily fail.
Recovered the3 passive classes from tracked HEAD schemas.py, with the existing149 finish149_boundaries.py extraction identifying the unchanged intended class bodies; retained CASE request export from separate contracts_case_short.py. Restored app imports/OpenAPI200/all3 public reservation schema names/new weight preview;193 actual root scenario and quality545/0/76/24/bothTS passed. Original untracked contracts.py had no saved pre-write bytes, so byte-for-byte recovery is not asserted. No old stock operation was reissued for repair.
Prevention: always inspect rg --files/direct existing path and contents before creating a facade. AST non-growing debt alone is not public export validation; meaningful API startup/import check after contract extraction. No generalized testing project added.
"""
for path,line in [
("wiki/index.md","- [Потребность после принятого отклонения](database/retailcase_ni042_weight_demand_20261011.md):193 current.4 waiver/original10 preserved/return reopens10/no stock write."),
("wiki/index.md","- [Восстановление публичных DTO inventory](incidents/retailcase_inventory_contract_overwrite_20261011.md):192 mistaken facade overwrite repaired before193 stock case; API exports/quality confirmed."),
("wiki/log.md","2026-10-11:193 APPLIED current accepted weight deviation in existing pool math; CASE1071 original10/actual9.6/H9.6/waiver.4/remaining0, native return waiver0/demand10/historyretained. Restored accidentally overwritten192 public reservation DTOs; appOpenAPI200/quality5450cycles76debt24tests/bothTS. Indexed fast1.392ms/12 and decision17.851ms/2 bounded retained; inventory batching/plan owner."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:193 current accepted order weight deviation suppresses duplicate remaining demand; own original10/fact9.6/waiver.4/demand0, native return reopens10/history preserved. Default15 and ordinary NET completion delivered; lastwholebox8or12/planningvariableboxes/hardware/browser remain.")]:
 p=Path(path);out[str(p)]=out.get(str(p),p.read_text(encoding="utf-8"))+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"193_weight_demand.md")]="""# Qwen:193
Run ni042_order_weight_demand_case.py dedicated dev. Original10/actual9.6/H9.6/accepted.4 -> remaining0; native return restores remaining10/waiver0 while immutable approval remains. Independently test other related CASE return taking total outside frozen window, original order qty/source changes, repeated histories, own-line cap, old current SKU pct change preserving already accepted agreement, arbitrary unapproved ACCEPT_SHORT gives no weightwaiver. Ordinary pool math unchanged; same READ ONLY snapshot/actual marked identities. Native root rollback/outbox/concurrent replay192 retained. Batch/plan decision for bounded200rows2000PT200decisions. Import/OpenAPI public3 reservation DTOs after192 recovery.
"""
print(json.dumps(out,ensure_ascii=True))
