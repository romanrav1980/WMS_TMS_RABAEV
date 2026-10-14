from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-11_ni053_partial_final_receipt")
page="wiki/database/retailcase_ni053_partial_final_receipt_20261011.md"
out[page]="""# Окончательная приёмка принятой части и исходный заказ
297 переиспользует оригинальный STORE_RECEIPT, Barcode/marked-profile/exact UNIT parser и custody. Нового механизма приёмки магазина нет. Actual291ordinary/292marked onward296 cargoQty1 приняты; marked только одна единица/два QR. Native outerrollback/HTTP200-409/replay; stock events0/P0/UID рождения+шестьcodehashes unchanged. Existing admin receiver допускается текущей legacy GLOBAL_ADMIN семантикой; отдельный nonadmin/browser/independent297 case не проводился.

Обнаружен действительный пробел: OrderDelivery linking original(oldUID) и actual(newpartialUID) показывал accepted0 несмотря на final receipt1 и верную lineage. Исправлено через сохранённый onward receipt и APPLIED295 подтверждение transport shortage: originalUID→acceptedUID разрешено только exact originalLoad/receivedROOT/shippedActual1/expected3=actual1+loss2. Fullordinary/fullmarked flows keep originalUID behavior.

Проекция только при единственном originalowner даёт shipped3/accepted1/unreceived2/confirmed_transport_shortage2/statusPARTIALLY_ACCEPTED. Транспортная недостача входит в unreceived2; не выдаётся за goods accepted и не складывается повторно. Не совпадающее total или duplicate final lineage отклоняются; sharedpartial owner remains NEEDS_OWNER_ALLOCATION, без пропорционального угадывания. OriginalSHIP/FF3 не переписывается и не повторяется. Existing229 originalorder2030 accepted3/unreceived0/transportshort0 сохранён.

Raw order-delivery.js уже вызывался из order-execution, но DOM-панель отсутствовала в текущем customer-orders.html. Восстановлена одна панель существующей доставки: qty/confirmedtransportshort and original→final load/UID lineage, sender/API/actor/requestserial fences, auth-change clears. Target statusPARTIALLY_ACCEPTED остаётся прежним контрактом. Runtime browser не проведён.

Дополнительно confirmed loss book enforced directly by current RRL_STOCK_UNIT_GUARD for every native update, не только UNIT_CORE helper. Existing immutable birth/BASE/version/CTX/unit lock enforcement сохранены; sparse PHYSICAL_UNIT_KEY PK probe. Lost book keys cannot be ordinarily moved/restored; no loss status/QR mutation introduced. Trigger branch runtime corrective attempt not executed; no production correction claimed.

NativeAPI ALLVALID/architecture6290cycles76/TransportCoordination TS PASS/encodingPASS. Current source/fixture context297_291 and _292 receipts done; don't rerun birth/rollback tests aftercommits. Next explicit correction/recovery of confirmedlost units plus residual nested/aggregate/hardware/external/independent scope.

SQL: bounded requested original loads<=200 and legs/receipt<=2000, unique receipt/loss/op keys. tmp/slow297.json actual snapshot; maintain these existing indexed joins/bounds, no warehouse-wide cache/index added. 296 stats only additive loss tables reduced new incoming child secondpair to~5.995ms/~74.5buffers perread (cold first147.447ms); Native promise7.055ms/32buffers average6exec. Keep scoped200/predicates and refreshed journalstats, no broader capacity claim.
"""
for path,line in[
("wiki/index.md","- [Окончательная приёмка частичного межскладского товара](database/retailcase_ni053_partial_final_receipt_20261011.md):297 reused STORE qty1, original3/accepted1/unreceived2/confirmedloss2, explicit UIDlineage/oneowner/no guess."),
("wiki/log.md","2026-10-11:297 reused actualSTORE for291ordinary/292marked onward1 withQR2; rollback/race/replay/noStock. Fixed real OriginalUID→partialUID order projection under exactAPPLIED295transportloss provenance; original3/accepted1/unreceived2/confirmedloss2/PARTIALLY_ACCEPTED, sharedpartial remainsunallocated/duplicate lineage rejected. Restoredmissing existingcustomer-order delivery DOM panel+losscolumn+lineage/currentactor/API/serial. Native directUNIT_GUARD nowlossbook check (privateunithelperalready295), no unitstatus/codebirth/qtymutation. Existing229full3/protected20-20/sixcodes retained; no corrective runtime/browser/independentclaim."),
("wiki/runbooks/retailcase_active_work.md","LatestNative/app297/serv297: actualfinalSTORE291ordinary/292marked qty1 received, tmp/context297_291/_292 authoritative. Originalorder2049/markedorder fromcontext297 nowshipped3 accepted1 unreceived2 confirmedtransportshort2; originalFFunchanged. Existing2030accepted3 retained. Do NOT rerun initialNativeStoreRollback afterpublishedreceipts. Native unittrigger+helper bothconfirmed-loss book guards; sourceoldmissing2 historyimmutable. Next recovery/correction/remainingincrements; full18/external/independent notdone."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni05_3.md","11.10.2026:297 Existing STORE_RECEIPT accepted actualonward1 ordinary/marked2QR afterpartialwarehouse/loss2; no newengine. Fixed originalUID-to-newUID order credit:shipped3 accepted1 unreceived2 confirmedtransportshort2/PARTIALLY_ACCEPTED; originalfull229 preserved/sharedpartial no guessing. Existingdelivery panel restored. Recovery/nested/aggregate/independent remain."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md","11.10.2026:297 Partial291/292 two-leg actual1 nowaccepted by STORE originalrecipient flow, originalorder3 recordsaccepted1/unreceived2/confirmedcarrierloss2 without repeated fulfillment. Actualtwo-legpartial standalone dev reachesfinalreceipt; recovery/nested/aggregate/industrial/independent stillnotaccepted.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
for ident in["NI05.3","NI06.1"]:next(x for x in j["increments"]if x["id"]==ident).setdefault("implementedSlices",[]).append("297 reused finalrecipientqty1/marked2QR; originalUID-newUID exactconfirmedloss projection source3 accepted1 unreceived2 confirmedshort2/oneowner; actual291-292")
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));j["additional_scripts"].append("../2026-10-11_ni053_partial_final_receipt/001_unit_loss_guard.sql");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
out[(d/"002_ledger.sql").as_posix()]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-297-partial-final-recipient'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Confirmed loss key guard and existing final recipient partial shipment lineage',sysdate,user,'db/migrations/2026-10-11_ni053_partial_final_receipt/001_unit_loss_guard.sql','db/migrations/2026-10-11_ni053_partial_final_receipt/rollback.sql','APPLIED','Actual ordinary and marked accepted1 final STORE; original3/accepted1/unreceived2/transportshort2, same originalFF. Existing229 full3 preserved; currentlossbook guarded in direct nativeUNIT trigger. No stock/GovACK/independentclaim.');
commit;
"""
out[(d/"rollback.sql").as_posix()]="""declare n number;begin
 select count(*)into n from RRL_INTERWARE_SHORTAGE_UNIT;
 if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_CONFIRMED_LOSS_KEYS');end if;
end;
/
@@000_before_rrl_stock_unit_guard.sql
-- Revert order projection and raw delivery panel in the same release; preserve final receipt history.
"""
qroot=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(qroot/"NI05.3/297_partial_final_receipt.md").as_posix()]="""# Qwen297: конечная приёмка принятой части
Read wiki/database/retailcase_ni053_partial_final_receipt_20261011.md/tmp/context297_291/_292. Alreadyaccepted, do notrerunfixturebirth/outerrollbackpreconditions.
Replay actualSTORE exactID/body ->same result/singlefact/noStock. Original3 accepted1 unreceived2 confirmedtransportshort2, PARTIALLY_ACCEPTED; loss not goods. Original229order2030 full3 unaffected.
Shared originalowner partial requires explicitallocation; quantity2 insteadloss2 fails; duplicate lineage fails. Exact originalLoad/acceptedUID/actualQty/APPLIEDloss required beforecrediting newUID to original. All sixcodehashes/birth unchanged/missing2lossbook blocks ordinary unitmutation.
Browser existingcustomer-orders Deliverypanel exists, actor/API/order/requestserial clear/fence; showntransportshort2 is includedinunreceived2. Nativeordinary+marked realreceiver gate originallysame; independent nonadmin partial/browser/hardware/ERP/GovACK notcompleted.
"""
print(json.dumps(out,ensure_ascii=True))
