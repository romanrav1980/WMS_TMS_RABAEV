from pathlib import Path
import json
out={};a=Path("db/migrations/2026-10-11_ni072_regulatory_scope");b=Path("db/migrations/2026-10-11_transport_planned_default")
s252="""# NI07.2: сообщения маркировки в сверке исходного склада
252 extends existing DayReconciliation and raw day-reconciliation page, same current actor/WARE/READ ONLY snapshot and stock/ERP/operational backlog. No new queue/quantity writer.
RRL_EVENT_OUTBOX explicitly original payload warehouse_id scopes system/event/delivery-status groups, current registered SKU profile systems plusCRPT/EGAIS/Mercury and marked native event kinds; profiles removed later do not hide known native disposal/supplier events. Unknown unprovable source warehouse not guessed, coverage_complete=false. Root STOCK_OPERATION source checked APPLIED when applicable. No raw codes/payload/signatures/foreign global counts returned.
Delivery DONE/EXPORTED/ACKNOWLEDGED does not infer legal government acceptance in this report; government_acceptance=NOT_VERIFIED_BY_THIS_REPORT/government_ack_reconciled=false. Regulatory outstanding items visible separately from ERP and physical P/H. Multiple system messages are message counts only, never multiply physical quantity. Day remains not closed; actual lifecycle/real external ACK reconciliation is still pending.
Actual case252 reads own existingWARE51365792 as activeWR234 currentview: disposal236 andsupplier237 eachCRPT+EGAIS/currentrootAPPLIED, open ack items/no quantity inference. Foreign65691543403; actualadminHTTP matches samecurrentgroups. Protected20/20/no newgoods/users/fixtures. Startup stale worker initially returned oldshape; restartedrootserv.bat then200.
Meaningful slow SQL180.838ms/3 uncovered full JSONwarehouse scan, USER_IND_EXPRESSIONS noexistingexpression. Applied functional index RRL_EVENT_OUTBOX_WARE_I(json_value(PAYLOAD_JSON,'$.warehouse_id' returningnumber nullonerror)); other indexes arestatus/retry/target/aggregate/unique and do not cover this filter. PostDDL new cursor12.917ms/2. Keep this index/scopedgroup200failure; ownerfinance/integrations verifies largeware/cardinality/archive before raising limits, no production load claim.
Architecture5740cycles76/rawJSsyntax PASS/nativefunctional index applied. Native ddl ledger2026-10-11-252-regulatory-source-warehouse-index; no government delivery/stock commands performed.
"""
s253="""# ТМС: корректный DEFAULT статуса нового рейса
253 fixes actual RRL_TRANSPORT_TASK.CONDITION DEFAULT from eleven literal '?' to UTF8 'Спланирован'. No old row mass repair. Original RRL_TRASPORT_TASK_ADD omits CONDITION and uses this default; native auto-plan/cluster/legacycallers therefore also get correct new status. 248 wrapper fix remains explicit current creation semantics.
Correction to earlier248 interpretation: captured function source does not contain the bad status literal. It omits column; liveUSER_TAB_COLUMNS.DATA_DEFAULT was '?'11. Raw captured000_legacy_add_evidence.sql remains untouched. Current default migration is central source, not an Oracle export rewrite.
Actual case253 asserts exactCyrillic DATA_DEFAULT, calls original legacyfunction under metadata scope, observescorrectplanned row, rollsback and confirms noTTretained. Sequence gaps normal; no goods/event/stock change/protected20-20. Historical badstatuses not normalized without ownerdecision.
ALTERTABLE default invalidated18 native packagebodies plus tareparticipantspec through %ROWTYPE dependencies. Targeted spec then threepasses ONLYcurrentlyinvalid packagebodies recompile; nativeerrors/invalid check after. RootAPI restartedafterDDL to discard pooledstate before business commands. No fullschema stats/recompile unrelatedobjects/new DBcopy.
Migration2026-10-11-253-transport-planned-default; currentruntime startup mirrors correcteddefault and dependentrecompile. Original stocksinglewriter/root/sourceidentity unchanged. This is schema default correctness, not certification of driver/warehouse/route admission.
"""
out["wiki/database/retailcase_ni072_regulatory_scope_20261011.md"]=s252;out[str(a/"README.md")]=s252
out["wiki/database/transport_planned_default_20261011.md"]=s253;out[str(b/"README.md")]=s253
for folder,ident,description,notes in[
(a,"2026-10-11-252-regulatory-source-warehouse-index","Regulatory day board source warehouse and matching functional JSON index","Existing236-237 sourceWARE51365792 CRPT-EGAIS/currentAPPLIED/foreign403/no qty/ACK inference. Old query180.838ms3/new12.917ms2/explicit index after metadata check. Architecture5740cycles76/JS/protected20-20."),
(b,"2026-10-11-253-transport-planned-default","Correct UTF8 default planned status for original new transport tasks","Native column default was literal questionmarks; original addfunction omitsstatus. Future insertscorrect/nooldmassrepair/directoriginalfunction rollback/noTTretained/protected20-20. Rowtype dependencies recompiled/pool restarted.")
]:
 out[str(folder/"003_ledger.sql")]=f"""merge into RRL_SCHEMA_MIGRATIONS d using(select '{ident}'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'{description}',sysdate,user,'{folder.as_posix()}/apply.sql','{folder.as_posix()}/rollback.sql','APPLIED','{notes}');
commit;
"""
 out[str(folder/"apply.sql")]=(folder/"apply.sql").read_text(encoding="utf-8")+("@002_recompile.sql\n"if folder==b else"")+"@003_ledger.sql\n"
out[str(a/"verify.sql")]="select INDEX_NAME,STATUS from USER_INDEXES where INDEX_NAME='RRL_EVENT_OUTBOX_WARE_I';\n"
out[str(b/"verify.sql")]="select DATA_DEFAULT from USER_TAB_COLUMNS where TABLE_NAME='RRL_TRANSPORT_TASK'and COLUMN_NAME='CONDITION';\nselect OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%';\n"
p=Path("wiki/database/retailcase_ni081_trip_time_20261011.md");s=p.read_text(encoding="utf-8")
s=s.replace("original legacy RRL_TRASPORT_TASK_ADD source stored status as11literal question marks","newly created original legacy row had status as11literal question marks;253 later proved the function omits CONDITION and the damaged literal was the table DEFAULT")
out[str(p)]=s+"\n253 source correction: original legacy function did notwrite the badliteral; table CONDITION DEFAULT containedit. Default now corrected centrally for futurealloriginalcallers, oldrows unchanged; originalfunction directrollback verified.\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
out[str(b/"000_before_manifest.json")]=p.read_text(encoding="utf-8")
m["startup_scripts"].extend(["../2026-10-11_ni072_regulatory_scope/001_index.sql","../2026-10-11_transport_planned_default/001_default.sql"])
m["additional_scripts"].append("../2026-10-11_transport_planned_default/002_recompile.sql")
out[str(p)]=json.dumps(m,indent=2)+"\n"
for path,line in[
("wiki/index.md","- [Регуляторная очередь в сверке склада](database/retailcase_ni072_regulatory_scope_20261011.md):252 sourcewarehouse/currentrootAPPLIED/messagecounts/notgovACK/functional index180→12.917ms."),
("wiki/index.md","- [DEFAULT нового рейса](database/transport_planned_default_20261011.md):253 correctUnicode plannedstatus/alloriginalcallers future/no oldmassrepair/directrollback; corrected earlier source attribution."),
("wiki/log.md","2026-10-11:252 same current DayReconciliation snapshot now source-scoped regulatoryqueue/profiles/system/status/currentrootproof/no rawcodes/noqty or governmentACK inferred. Existing236-237 ownWARE51365792/CRPT-EGAIS/foreign403/HTTP200/nofixtures/protected20-20. JSONWAREindex verifiedabsent/applied/180.838ms3→12.917ms2 boundedquery; architecture5740cycles76/JS. 253 corrected actual tableCONDITION DEFAULT '?'11 toUTF8planned forfuture originallegacy/nativeautoplan creation. Earlier248 blamedfunctionliteral incorrectly; livefunction omitscolumn, capturedsource kept. Originalfunctiondirectrollbackcorrect/noTTretained/oldrowsunchanged; rowtypeinvaliddependencies recompile andAPIrestart. Native manifests mirrors indexes/default/recompile."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni07_2.md","11.10.2026:252 originalwarehouse-linked regulatorqueue/currentrootproof/messagecounts/no govACK inference integrated same dayboard. Existingdisposal236/supplier237 CRPT-EGAIS/currentownview/foreign403/HTTP; field-index180→12.917ms. Actualprovider lifecycle/realACK/closure remain.")
]:
 p=Path(path);out[path]=out.get(path,p.read_text(encoding="utf-8"))+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"]if x["id"]=="NI07.2").setdefault("implementedSlices",[]).append("252 source-warehouse regulatory queue/current APPLIED source proof/scoped messagecounts/no govACK inferred/functional JSONWARE index")
next(x for x in j["increments"]if x["id"]=="NI02.2").setdefault("implementedSlices",[]).append("253 central original TT planned-status UTF8default corrected for future legacy/autoplan callers/no historical mass repair")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[str(root/"NI07.2"/"252_regulatory_scope.md")]="# Qwen:252 — очередь маркировки в сверке\nCurrentwarehouse beforegroups/same READONLYsnapshot/exact payloadwarehouse source/currentAPPLIED Root whereapplicable. No rawcode leakage/profilemultiplier quantity/DONE governmentACK inference. Coverageincomplete for unattributedsource; countsseparatemessages. Existing236-237 CRPT-EGAIS ownWARE/foreign403/nofixtures/physical20-20. Functional JSONWARE index absentbefore/liveafter/180→12.917ms. IndependentDONE-delivered-but-notACK andotherconfiguredsystem/200overflow cases.\n"
out[str(root/"NI02.2"/"253_planned_default.md")]="# Qwen:253 — default планового рейса\nLive DATA_DEFAULT exactUnicodeplanned; originalfunction omitsCONDITION. New native/manual/auto-plan/cluster/legacy callers mustgetplanned status; no historicmassupdate. Directoldfunctionrollbackcase leavesnoTT/stock. 248 priorfunctionliteralblame correctedinwiki; capturedrawsourceuntouched. TableDDL rowtypeinvalidrecompile onlyaffected/PooledAPIrestart/nativeVALID. Existingwrapperexplicitstatus preserves creator. ManifestmirrorsDefault/index startup.\n"
print(json.dumps(out,ensure_ascii=True))
