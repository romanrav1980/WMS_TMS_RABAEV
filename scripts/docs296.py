from pathlib import Path
import json,re
out={};d=Path("db/migrations/2026-10-11_ni061_partial_custody");before=Path("db/migrations/2026-10-11_ni061_shortage_disposition")
page="wiki/database/nicora_ni061_partial_custody_20261011.md"
out[page]="""# Завершение первого плеча и отправка принятой части
296 расширяет существующий INTERWARE_CUSTODY_RELEASE. Partial291/292 receipt требует APPLIED независимый295 confirm и точное immutable declared3=actualaccepted1+confirmedshort2/original source load/root/warehouse/request. Ответственность заканчивается отдельным native command effectiveAt=actualconfirm.CreatedAt, а не задним числом выгрузки. NativeLoadFact guard проверяет подтверждённое расхождение и retains original departed load/archive.

Существующий NEXT uses APPLIED partial receipt subset1 для marked currentBASE/UOM/UID/cell/version/status AVAILABLE вместо whole manifest3; originalSTconstructor выдаётqty1, same assignment/QC/LOAD/DEPART. Native departure requires acceptedRoot/acceptedQty actual LOADED and accountedshort2; полный original count3 не объявляется физически полученным. Read incoming distinguishes receipt_complete0 /shortage_resolved1 /confirmedshort2 /quantity_to_load1/actualloaded1. Coordination/UI separates fullreceived+placed from acceptedfragment+resolved discrepancy. No legal/operational admission fabricated.

Фактические ordinary291/marked292: custody outerrollback restoredNULL; parallel HTTP200/409 one actualrelease+exactrepeat; constructor createdone onwardSTqty1/no repeated originalFF. Initial original test vehicle type10 refused by existing address type15 guard; registered only own NEW target vehicles type15 with existing vehicle constructor, selected them through validated trip editor. Globaladdress/source archived vehicles untouched; no guard bypass.

Both onwardST assigned viaexistingNativePlan, existing QC (marked selected1/two codes), actual LOAD P1→0, Nativepromise/read incomingReady true while receipt_complete0/confirmedshort2. Existing NativeDEPART performed and exact replay saved. Original six code hashes byte-identical; source missing2 remainISSUED with lossbook2, received1 newlyISSUED under acceptedUID. Protected20/20 unchanged. tmp/context296_291.json and _292 actualcustody/ST/load/depart done. Do NOT rerun fixture source or predeparture rollbackcases aftercommit.

Partial loss clarification: loss does not reverse original fulfilled SHIPPED3; final recipient must acknowledge actual delivered1 and preserve commercialmissing2 without repeatingFF. No automatic resupply; originalSAP source/obligation remains evidence. Next final partial STORE acknowledgement and explicit recovery/correction of found lost units. Browser/independent/Gov/legal/hardware acceptance remain unperformed.
SQL: same selected receipt/claim PK, exact UNIT keys and scoped <=200incoming. tmp/slow296.json current measurements. Keep these bounds/PK and originaldirectional gate; broader capacity not claimed.
"""
for path,line in[
("wiki/index.md","- [Ответственность и отправка принятой части](database/nicora_ni061_partial_custody_20261011.md):296 original core/custody+existingST/QC/load/depart actual1, confirmedmissing2 preserved."),
("wiki/index.md","- [Проект движения после недостачи](database/nicora_ni061_partial_custody_design_20261011.md):296 accepted+confirmedshort accounting without false fullreceipt."),
("wiki/log.md","2026-10-11:296 current nativecustody after exactAPPLIED295loss/source match, loss timestamp and LoadFact guard; partial markedNEXT receipt subset, departuregateactualacceptedRootQty +confirmedshort; scopedincoming andCoordination/UI honestfullvsaccounted. Actual291/292 rollback/200-409/replay/oldconstructorST1/assign/QC/LOADP0/nativeDEPART. Existing type10/address15 refused; own NEWtype15vehicles selected original editor, globaladdress/sourcearchive untouched. Sixcodehashes/protected20-20 preserved. Next finalrecipient actual1/commercialmissing2/recovery. No external/independent/legal acceptance."),
("wiki/runbooks/nicora_active_work.md","LatestNative/app296/serv296b beforelastUI/aggregate edits: both291/292 fragments qty1 onwardDEPARTED; tmp/context296_291.json/_292 authoritative actualcustody/ST/load/depart. Never rerun case296_onward afterdepart because initial readiness expectsLOADED; replay departed finish296 safe. Missing2 confirmed295/markedlossbook2, sourceoldunitsISSUED/newacceptedunitISSUED/all6codes retained. Whole all18 stillnotaccepted; next final STORE qty1 acknowledgment/original3missing2 +lost recovery correction. Manifest296 current source/sourcecaptured only, noDBcopy."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md","11.10.2026:296 Partial receipt1+independentconfirmedloss2 разрешает отдельное завершение ответственности и прежние ST/QC/LOAD/DEPART только на actual1. Ordinary291/marked292 actualtwo-legpartial dev прошли; fullreceipt0 сохранён, источник/FF3 не переписаны/коды6 сохранены. FinalpartialSTORE/recovery/nested/independent остаются.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("296 existingcustody accepted1+confirmedshort2, markedreceipt subset, existing ST/QC/LOAD/DEPART1/currentread distinguished fullreceipt0; actual291-292");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));base="../2026-10-11_ni061_partial_custody/"
for pkg,name,body in[("RRL_STOCK_INTERWARE_CUSTODY","006_custody_current.sql","001_custody_body.sql"),("RRL_STOCK_INTERWARE_NEXT","007_onward_current.sql","002_onward_body.sql"),("RRL_INTERWARE_DEPART_GATE","008_depart_current.sql","003_depart_gate.sql")]:
 sources=[n for n in j["components"]if re.search(r"create\s+or\s+replace\s+package\s+"+pkg+r"\s",(out.get((p.parent/n).resolve().relative_to(Path.cwd()).as_posix()) or (p.parent/n).read_text(encoding="utf-8")),re.I)]
 assert len(sources)==1,(pkg,sources)
 out[(d/name).as_posix()]=(before/("000_before_"+pkg.lower()+"_package.sql")).read_text(encoding="utf-8")+"\n"+(d/body).read_text(encoding="utf-8")
 j["components"][j["components"].index(sources[0])]=base+name
j["additional_scripts"]+=[base+n for n in["001_custody_body.sql","002_onward_body.sql","003_depart_gate.sql","004_load_guard.sql"]]
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
out[(d/"005_ledger.sql").as_posix()]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-296-partial-custody-onward'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing first-leg custody and actual accepted fragment onward after confirmed shortage',sysdate,user,'db/migrations/2026-10-11_ni061_partial_custody/001_custody_body.sql','db/migrations/2026-10-11_ni061_partial_custody/rollback.sql','APPLIED','Ordinary and marked accepted1+confirmedshort2, actual custody rollback/race/replay/ST1/assigned/QC/load/depart, fullreceiptfalse. Source archive andsixcodes retained/protected20-20. Finalrecipient/recovery/independent pending.');
commit;
"""
out[(d/"rollback.sql").as_posix()]="""declare n number;begin
 select count(*)into n from RRL_INTERWARE_CUSTODY_PROOF f join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=f.RECEIPT_OPERATION_ID where r.ORIGINAL_ROOT_UID is not null;
 if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_PARTIAL_CUSTODY');end if;
end;
/
@@../2026-10-11_ni061_shortage_disposition/000_before_rrl_stock_interware_custody_package_body.sql
@@../2026-10-11_ni061_shortage_disposition/000_before_rrl_stock_interware_next_package_body.sql
@@../2026-10-11_ni061_shortage_disposition/000_before_rrl_interware_depart_gate_package_body.sql
@@000_before_load_fact_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
"""
qroot=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(qroot/"NI06.1/296_partial_custody.md").as_posix()]="""# Qwen296: принятую часть дальше, недостачу отдельно
Read wiki/database/nicora_ni061_partial_custody_20261011.md and tmp/context296_291/_292. Already departed; do NOT rerun source/initial custody/onward-load readiness cases.
Replay actualcustody/onward/depart ->same result/no duplicateFF/P/units. Exact source_qty3 accepted1 confirmedshort2; fullreceiptfalse. Own fresh partial fixture without confirmedloss mustdenyrelease/depart; foreign/mismatchedloss/qty/UID deny. Markedsubset usesonly accepted1/two profiles QC, missing2book preserved. SourceLoadarchive and originalorderSHIPPED3 retained; no fakefullcustomer delivery. Current postDEPART incoming phase isn't LOADED ready, correct.
Browser shows fullreceived/placed separately from acceptedfragment+resolved; durable currentactor/API intent; address type guard preserved. Next finalSTORE ack1/missing commercial2 and correction of recoveredlostunits; no GovACK/hardware/legal claim.
"""
print(json.dumps(out,ensure_ascii=True))
