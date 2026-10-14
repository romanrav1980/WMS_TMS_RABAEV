from pathlib import Path
import json
out={};base="db/migrations/2026-10-11_ni061_shortage_disposition/"
page="wiki/database/nicora_ni061_shortage_disposition_20261011.md"
out[page]="""# Независимое подтверждение транспортной недостачи
295 реализует [[nicora_ni061_shortage_disposition_design_20261011]]. Два zero-stock-effect владельца INTERWARE_SHORTAGE_REPORT/CONFIRM подключены к единственному RRL_STOCK_POSTING_API. Current target actor/right и разделение автор/согласующий до cached reply и после actual wait. Один immutable report/receipt, confirm/request/receipt, exact partial difference, missing frozen unit subset/current issued source/UOM/version/reservation. Shared policy/config и sorted OP10/ROW20/HU30/UNIT60/UNIQUE70; no CFG6 или запас50/глобальный складской mutex.

RRL_INTERWARE_SHORTAGE_REQUEST/FACT/UNIT и captured-transaction direct-DML guards; atomic common journal/domain+confirmed missing-unit book/SAP intent/common outbox. Warehouse P/H не изменяются: уже состоявшаяся source shipment выдала полный товар, actual partial receipt создала только1. Нет повторного списания2. Исторические единицы остаются ISSUED и коды сохраняются; общий private unit mutation guard now blocks confirmed missing keys pending explicit correction. Реальная внешняя операция/ACK не выдуманы.

API POST shortage-reports /shortage-confirmations; typed strictquantity/reason/evidence. Existing raw interwarehouse UI first loads same receipt reconciliation; report and confirmation permissions separate, immutable intent saved before HTTP/retry, current actor/API/receipt and pending protection. Reader shows report/author/current confirmation/approver/evidence separately from warehouse quantity and responsibility.

Фактические291 ordinary и292 marked: report outerrollback; same actor confirmation20882; two separate transactions required by existing DIRTY_TRANSACTION discipline; real own CAL264 reporter temporarily activated in target WARE, restored retired/right/WARE unchanged after case. Independent admin confirmation outerrollback removed book/fact/outbox. Published HTTP concurrent200/409 created one confirm each; exactreplay/collision passed. Marked two missing keys booked, all six original code hashes unchanged, acceptedP1H0/sourceP0/protectedP20H20. Custody stillopen. Common private mutation guard loss branch established in source; separate restorative command runtime case not executed.

SQL evidence tmp/slow295.json: bounded missing<=10000/key-unique/code origin indices; same selected receipt, no full warehouse scans. Maintain PK and capped subset. Large marked subset JSON anti-join plan/CPU optimization belongs inventory owner before million-operation capacity claim; no load gate or industrial acceptance claimed. Browser/independent/gov remains unperformed. Next296 explicit first-leg custody resolution accepted+confirmedshort=declared and next leg only actualaccepted1. Late recovered goods requires explicit correction, not editing history.
"""
for path,line in[
("wiki/index.md","- [Независимый акт транспортной недостачи](database/nicora_ni061_shortage_disposition_20261011.md):295 same native core/report+otherapprover/actual ordinary-marked short2/no repeat deduction."),
("wiki/index.md","- [Проект подтверждения недостачи](database/nicora_ni061_shortage_disposition_design_20261011.md):295 loss book and current resources;296 explicit acceptedfragment custody next."),
("wiki/log.md","2026-10-11:295 report/confirm zeroqty commands installed in canonical root; immutable request/fact/missingunit book, currenttargetscope before replay/afterwait, independent actor, exact missing subset/version/UOM, UNIT60 + row/unique source locks; common journal/SAPintent/outbox oneUOW. Ordinary291/marked292 reportrollback/distinct actualreporterCAL264 restored retired/confirmrollback/200-409/replay/collision/P1H0/source0/protected20-20. DIRTY_TRANSACTION correctly requires separately committed report/confirm. No custodyrelease/GovACK/industrial/independent claim; next296."),
("wiki/runbooks/nicora_active_work.md","LatestNative/app295/serv295: actual291/292 short2 independently confirmed; tmp/context295_291.json +tmp/context295_292.json actualreportCAL264 (restoredretired)/actualconfirmadmin. Do NOT rerun case295_native after publishedfacts; exactreplay case295_commit safe. Custody remainsNULL; P1/H0 receivedfragment unchanged. Native manifests/bundle295 generated FILES only. Unitcore lossbook guard blocks ordinary mutation of confirmed missing keys; next296 custody/acceptedfragment onward."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md","11.10.2026:295 Акт транспортной недостачи и независимое подтверждение реализованы через единое ядро. Ordinary291/marked292 short2 подтверждены другим согласующим, missing2 keys booked/коды сохранены/acceptedP1/без повторного списания. Ответственность и выезд ещё не освобождены: следующий296."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni06_2.md","11.10.2026:295 Транспортная потеря между складами теперь фиксируется отдельным неизменяемым актом и независимым подтверждением без повторного складского списания. Это не физическое списание складского quarantine DISPOSAL; исходные коды/quantity сохраняются, внешняя квитанция отдельно.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("295 native report-independentconfirm carrier shortage exactissuedmissingkeys/no secondPdeduction/request+fact+unitbook/SAPintent/commonoutbox; actual291-292 short2");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
qroot=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(qroot/"NI06.1/295_shortage_disposition.md").as_posix()]="""# Qwen295: независимый акт транспортной недостачи
Прочитать wiki/database/nicora_ni061_shortage_disposition_20261011.md и tmp/context295_291.json/context295_292.json. Не перерождать источники и Native rollback-case295 после published confirmations.
1. Точный actualconfirm повтор ->saved result/onefact/noP. Changedqty/body sameID409/new confirm409.
2. CurrentTarget+store_return_approve обязательны beforecache/afterwait; same reporter forbidden evenGLOBAL_ADMIN. CAL264 retired ->reject/no credentialreset.
3. Own fresh fixture only: reportrollback, separately commitreport before independentconfirm (DIRTY_TRANSACTION forbids composing separate top-level commands), confirm outerrollback removesfact/book/outbox.
4. Exact ordinary/marked missing qty/UOM/keys/version/source/ISSUED/unreserved; changed missingstate fails. Original codes/BASE/birth preserved; Booked missing keys cannot be ordinarily restored/moved before corrective command. No synthetic physicalwarehouse stock orGovACK.
5. UI report/confirm rights, loaded receipt, actor/API switch, durable beforePOST/retry. Browser independent case unperformed. Actual custody must remainopen until explicit next296.
SQL large subset <=10000 anti-join plan inspection is a targeted backlog, not reason to label capacity passed.
"""
out[base+"007_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-295-interware-shortage-disposition'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Independent carrier shortage report and confirmation via existing stock root',sysdate,user,'db/migrations/2026-10-11_ni061_shortage_disposition/001_schema.sql','db/migrations/2026-10-11_ni061_shortage_disposition/rollback.sql','APPLIED','Actual ordinary and marked partial short2 independently confirmed; rollback/race/replay/collision, acceptedP1/source0. No repeated stock deduction/custody release/GovACK. Missing-unit book blocks ordinary mutation pending correction.');
commit;
"""
out[base+"rollback.sql"]="""declare n number;begin
 select count(*)into n from RRL_INTERWARE_SHORTAGE_REQUEST;if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_SHORTAGE_HISTORY');end if;
end;
/
@@000_before_rrl_stock_posting_api_package_body.sql
@@../2026-10-11_ni061_marked_partial/001_unit_core.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
-- Preserve additive empty tables for current read projections; revert app/UI before schema removal.
"""
print(json.dumps(out,ensure_ascii=True))
