from pathlib import Path
import json
out={};page="wiki/database/nicora_ni053_lineage_lookup_20261011.md"
out[page]="""# Поиск окончательной приёмки по исходной погрузке
298: у RRL_INTERWARE_ONWARD_DISPATCH отсутствовал SourceLoad-leading индекс. Current order delivery reader297 averaged70.349ms/6278buffers total3 executions. Added nonunique RRL_IW_DISPATCH_SOURCE_IX(SOURCE_LOAD_OPERATION_ID,OPERATION_ID), NativeVALID +only table stats. Scoped requested load CTE uses original SourceLoad and explicit nested loops; final receipt/line/partialreceipt/loss/operation/issue joins kept same snapshot/bounds200loads/2000lines.

New actual child7rgr40512bfwq avg20.529ms/146buffers total3 executions versus prior8g0v4nd7bd72b70.349ms/6278buffers. Full229customer2030 accepted3 and partial297customers accepted1/confirmedloss2 exactlysame; no records changed. Decision: keep source index/boundedNL, no full warehouse scan/cache/extra broad load test. Owner delivery monitors sparse source key lookup when archive grows; these dev figures do not establish million-operation capacity.

SQL db/migrations/2026-10-11_ni053_lineage_lookup/001_index.sql applied RABAEV/orcl. Bundle startup index only generatedFILES, full stock refresh not applied. Raw order-delivery pane now exists; source code guard catcheslate errors byrequestserial too. No new engine/warehouse registry.
"""
for path,line in[
("wiki/index.md","- [Поиск приёмки по исходной погрузке](database/nicora_ni053_lineage_lookup_20261011.md):298 missing source index/NL,70.349ms6278buf→20.529ms146buf total3, exactfull/partialprojection preserved."),
("wiki/log.md","2026-10-11:298 fixed real nonindexed SourceLoad linkage in onwarddispatch; SourceLoad/OPID nonuniqueindexVALID+table stats/scoped requested-source NL and original currentjoins. Threeactual reads full229 andpartial291/292 preserve accepted3 versus1/confirmedloss2, average70.349→20.529ms/totalbuffers6278→146. No qty/history/source changes or industrial capacityclaim."),
("wiki/runbooks/nicora_active_work.md","LatestApp298/native297+source index298/serv297 before finalreadhint/UI changes. NativeALLVALID/app6290cycles76/TransportCoordinationTS PASS/encodingPASS. SourceLoad lineage sparseindexVALID boundedNL; slow298 avg20.529ms146buf total3vsold70.349ms6278buf. Next confirmedlostgoods recovery/correction design+single-core functionality, no duplicate supplierReturn engine.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/runbooks/nicora_active_work.md");s=out[p.as_posix()]
s=s.replace("Native manifest280: time materialV2/approval256, original route estimate259, regulatorywarehouseindex252, plannedDEFAULT253, awarefutureTaskFinish254.","Native manifest298: TIME sourceV5 (287), canonical stock root295/UnitCore295/unittrigger297, partial custody-NEXT-depart296, SourceLoad index298. Original route estimate259/regulatorywarehouseindex252/plannedDEFAULT253/awarefutureTaskFinish254 retained.")
s=s.replace("App283/APIserv283,","App298/APIserv297 (restart for finalreaderhint),")
out[p.as_posix()]=s
p=Path("wiki/index.md");out[p.as_posix()]=out[p.as_posix()].replace("current native293/app293/","current native298/app298/")
p=Path("wiki-raw/wms_admin_ui_reference/order-delivery.js");s=p.read_text(encoding="utf-8");s=s.replace('if(orderState.selectedId===orderId&&scope===','if(serial===orderDeliveryGeneration&&orderState.selectedId===orderId&&scope===',1);out[p.as_posix()]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));j["startup_scripts"].append("../2026-10-11_ni053_lineage_lookup/001_index.sql");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
base="db/migrations/2026-10-11_ni053_lineage_lookup/"
out[base+"002_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-298-final-lineage-source-index'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Bounded final receipt source-load lookup',sysdate,user,'db/migrations/2026-10-11_ni053_lineage_lookup/001_index.sql','db/migrations/2026-10-11_ni053_lineage_lookup/rollback.sql','APPLIED','SourceLoad OPID indexVALID, native stats; scoped NL exactsame full andpartialprojections. Avg70.349ms6278buffers to20.529ms146buffers total3; no stock/historychanges.');
commit;
"""
out[base+"rollback.sql"]="""-- Restore previous bounded reader hints in same release before dropping named index.
drop index RRL_IW_DISPATCH_SOURCE_IX;
"""
print(json.dumps(out,ensure_ascii=True))
