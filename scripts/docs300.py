from pathlib import Path
import json,re
out={};d=Path("db/migrations/2026-10-11_ni061_loss_recovery");page="wiki/database/retailcase_ni061_loss_recovery_receiving_20261011.md"
out[page]="""# Фактическая корректирующая приёмка найденного остатка
300: INTERWARE_SHORTAGE_RECOVER private RRL_STOCK_IW_RECOVERY_REC behind same RRL_STOCK_POSTING_API. Current targetreceiver/interwarehouse_receive beforecache-afterwait; exact APPLIED independent299approval/sourceQty2/SKU/UOM/oldUID/source currentlost keys/version/reservation +newpallet/cell/item scans/gross/reason/document. Whole remainder only; ordinary and UNIT-marked standalone. Receiving cell requires ownWARE/accept0/remainsBlocked1/replenishmentBlocked1. No available allocation until separate placement.

Reuses private RRL_STOCK_INTERWARE_PART source lot/expiry/production/price/naklad/origin clone and existing balance.apply_delta/write_leg; exact same existing receive_partial_issued unit subset method now admits separately captured recovery command. No new inventorywriter orcodebirth. Sharedfences/sorted OP10/ROW20/HU30/stock50 old+new+origin/UNIT60/unique70. Short oneUOW: newlot+P2/event+recoveryreceipt/unit proof+originalunit move+SAPintent/commonoutbox; no innercommit/network.

Immutable recovery receipt/unit proof lets existing confirmed-loss helper and directUNIT trigger permit only exact current IN_FLIGHT recovery or previously APPLIED recovery of that same book fact+key. Remaining unrecovered loss keys stillblocked. Raw oldloss fact/book/codes remain; recoveries shown separately. Other native writers cannot restore blockedkeys withoutproof. First receipt quantity1/history is never changed and recovery isn't customeracceptance.

Actual291ordinary/292marked source remaininglost2: nativeouterrollback removednewP2/pallet/recoveryfacts/units/outbox and restoredoldISSUED2. Missing one of4 requiredQR denied; HTTP concurrent200/409 producedone actualreceipt/newUID/P2H0 each, exact replay andqtycollision. Marked oldkeys2 movedAVAILABLE/newUID/version+1, allsix originalcodehashes byte-identical. Source oldstock0; protected20/20. Case300currentreader returnsrecovered2/netunrecovered0/currentmissing0/no stateconflict, receivingcell1/1 blocksallocation. Originalcustomeraccepted1 remains; noGov/ERP externalACK.

API recovery-receipts typedscans/currentapproval; rawpanel uses same pending actor/API command savedbeforePOST, exact source/newPAL/cell/item/gross/evidence +profile QR. Scanner draft before submit heldinmemory; submitted uncertain command includingcodes durable withsameOPID. Browser/hardware/independent notconducted. Next existing placement/recovery-specific shipment and summedfinalreceipts, partial/repeatedloss history. No wholeNI06 acceptance or physicaldeviceclaim.

SQL: actual recoveryunit INSERT12.514ms/4exec303buf; booked-key private5.436ms/4exec122buf anddirect2.599ms/4exec51buf; recoverykeysreader14.274ms/2exec57buf includesnewjournal cold parse. Maintain selectedreceipt/loss and keyPK/bounds10000, no extra cache/globalmutex. Ownerinventory shouldbatch repeatedunit probes if large measuredcase establishes CPU bottleneck; currentmillion-capacity notclaimed.
"""
for path,line in[
("wiki/index.md","- [Корректирующая приёмка найденного товара](database/retailcase_ni061_loss_recovery_receiving_20261011.md):300 samecore actualP2/newUID/old2units4QR/all6codes retained/quarantine/no customerACK."),
("wiki/log.md","2026-10-11:300 native wholelost remainder actualRECOVERY via existingPART/balance/leg/unit subset; private source/currentWARE/scans/exactAPPLIED299approval/lostkeys versions/shared sorted old-newstock+units; captured recoveryguard proof unlocksonly restoredkeys, immutableloss retained. Actual291ordinary/292marked outerrollback/QRmissing/race/replay/collision/P2H0/old2keysAVAILABLE/all6codehashes/protected20-20. Readerrecovered2/net0/history/currentmissing0/quarantineblocked; rawdurable receivingpanel. No customerreceipt/GovACK/independent/hardware acceptance; nextplacement/redelivery/partial-recurring scope."),
("wiki/runbooks/retailcase_active_work.md","LatestNative/app300/serv300 beforefinalreader/UI edits: tmp/context300_291/_292 actualrecoveryP2H0 intoIR291/IR292/newIDs inreceipt_result, marked2AVAILABLE/oldbirthsixcodes unchanged. NEVER rerun case300_native aftercommittedrecovery; case300_commit replay safe. Wholelost2-only recovery, Root019/Unit015/guard016/Pallet017 current. Stock3 originalinitial redistributed: buyeraccepted1 +warehouseRecovered2; no newunitbirth. NativeallVALID/app6290cycles76; next placement/supplemental shipment and summedfinalreceipts/partial-recurrent lifecycle. Manifest300 generatedFILES only."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md","11.10.2026:300 Фактическое восстановление всего ранее недостающего остатка2 проведено originalcore: ordinary/marked2keys4QR/P2H0/newUID/прежние коды6. Sourceqty1receipt/lossfacts сохранены, карантиннедоступендляотбора. Partial/recurrent recovery, placement/redelivery, nested/aggregation и независимая приёмка остаются."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_2.md","11.10.2026:300 Найденный после транспортной недостачи товар восстанавливается корректирующей приёмкой через тотжеядро, без повторного рождения маркированных единиц/правки истории. Actuallost2 ->P2/quarantine under independentapproval; конечная доставка ещё отдельная.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_shortage.py");s=p.read_text(encoding="utf-8")
s=s.replace('unresolved=[k for k in unresolved if k not in recovered_keys]','''unit_by_key={u["key"]:u for u in units}
            unresolved=[k for k in unresolved if k not in recovered_keys or
                unit_by_key[k]["current_quantity"]is None or Decimal(unit_by_key[k]["current_quantity"])!=Decimal(unit_by_key[k]["declared_quantity"])or
                unit_by_key[k]["current_base_uom"]!=unit_by_key[k]["base_uom"]or unit_by_key[k]["current_stock_status"]not in {"AVAILABLE","BLOCKED","ISSUED"}]''',1)
out[p.as_posix()]=s
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("300 samecore actualwholeconfirmedlost2 recovery/newUID/P2/quarantine/marked2oldkeys4QR/all6codes/no birth; nextplacement/redelivery/partial-recurrent");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"));base="../2026-10-11_ni061_loss_recovery/"
def read(n):return out.get((p.parent/n).resolve().relative_to(Path.cwd()).as_posix())or(p.parent/n).read_text(encoding="utf-8")
for pkg,name,spec,body in[
("RRL_STOCK_BALANCE_CORE","020_balance_current.sql","011_balance_spec.sql","000_before_rrl_stock_balance_core_package_body.sql"),
("RRL_STOCK_LOCATION_CORE","021_location_current.sql","012_location_spec.sql","000_before_rrl_stock_location_core_package_body.sql"),
("RRL_STOCK_INTERWARE_PART","022_part_current.sql","013_part_spec.sql","000_before_rrl_stock_interware_part_package_body.sql"),
("RRL_STOCK_UNIT_CORE","023_unit_current.sql","014_unit_spec.sql","015_unit_body.sql"),
("RRL_STOCK_POSTING_API","024_receiving_root_current.sql","000_before_rrl_stock_posting_api_package.sql","019_receiving_root_body.sql")]:
 sources=[n for n in j["components"]if re.search(r"create\s+or\s+replace\s+package\s+"+pkg+r"\s",read(n),re.I)]
 assert len(sources)==1,(pkg,sources)
 out[(d/name).as_posix()]=(d/spec).read_text(encoding="utf-8")+"\n"+(d/body).read_text(encoding="utf-8")
 index=j["components"].index(sources[0]);j["components"][index]=base+name
 if pkg=="RRL_STOCK_POSTING_API":j["components"].insert(index,base+"010_receiving.sql")
j["packages"].append("RRL_STOCK_IW_RECOVERY_REC")
j["additional_scripts"]+=[base+n for n in["011_balance_spec.sql","012_location_spec.sql","013_part_spec.sql","014_unit_spec.sql","015_unit_body.sql","010_receiving.sql","016_unit_guard.sql","017_pallet_guard.sql","018_receiving_guards.sql","019_receiving_root_body.sql"]];out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
out[(d/"025_receiving_ledger.sql").as_posix()]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-300-loss-recovery-receiving'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Physical corrective receipt of whole confirmed lost remainder via same kernel',sysdate,user,'db/migrations/2026-10-11_ni061_loss_recovery/010_receiving.sql','db/migrations/2026-10-11_ni061_loss_recovery/rollback_receiving.sql','APPLIED','Actual ordinary/marked lost2 ->newP2H0/quarantine, same two old units andsix originalcodes; native rollback/QRmissing/race/replay/collision. Historical loss intact, no customer/GovACK. Partial/recurrent and redelivery pending.');
commit;
"""
out[(d/"rollback_receiving.sql").as_posix()]="""declare n number;begin
 select count(*)into n from RRL_INTERWARE_RECOVERY_RECEIPT;if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_PHYSICAL_RECOVERY');end if;
end;
/
@@004_decision_root_body.sql
@@000_before_rrl_stock_balance_core_package.sql
@@000_before_rrl_stock_location_core_package.sql
@@000_before_rrl_stock_interware_part_package.sql
@@000_before_rrl_stock_unit_core_package.sql
@@000_before_rrl_stock_unit_core_package_body.sql
@@000_before_rrl_stock_unit_guard.sql
@@../2026-10-11_ni061_partial_receiving/007_sap_clone_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
"""
qroot=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(qroot/"NI06.1/299_300_loss_recovery.md").as_posix()]="""# Qwen299-300: найденный whole lost remainder
Read wiki/database/retailcase_ni061_loss_recovery_receiving_20261011.md, tmp/context299_291/_292 and context300_291/_292. ActualP2 alreadycommitted; NEVER rerun initial native rollbackcases/sourcebirth.
Exactactual recovery/approval repeats ->same onefact/P2; changedpayload409/new competingreceive409. MissingQR/profile/foreignSKU/UOM/sourcePAL/newPAL/cell/currentWARE rights/collision rejects no P. Ordinarynocodes permitted; marked two physicalunits require4profileQR.
Own fresh fixture: report/independentapproval separatetop-levelTx, physicalnativeouterrollback removesPAL/P/units/recoverybook/event/outboxes. Corrective proof lets only recoveredkeys normalmovement; stilllostkeys blockedbyhelperanddirecttrigger.
Actualrecovered2/sourceold0/buyeraccepted1 unchanged/sixcodehashes preserved/receivingcell rem+replenishblocked. UI actor/API/receipt change clearsdraft scope, pendingintent savedbeforeHTTP for exactretry. Current historical2 shortage and recovered2/net0 distinct from newcustomerreceipt.
Whole recovery only in current slice; partial/recurrent/corrective redelivery and external/independent/hardware notaccepted. Report actualtests separatefromstaticreview.
"""
print(json.dumps(out,ensure_ascii=True))
