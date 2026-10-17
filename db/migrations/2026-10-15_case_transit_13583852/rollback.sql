-- Empty-only paired rollback; quiesce CASE writers first. Never remove used transit history.
declare n number;begin
 RRL_STOCK_CONFIG_API.begin_change('admin','warehouse_settings_edit');
 select count(*)into n from RRL_REMAINS where CELL='CPT_13583852';
 if n!=0 then raise_application_error(-20886,'CASE_TRANSIT_CONTENT_HISTORY_PRESERVE_FORWARD_REPAIR');end if;
 select count(*)into n from RRL_CASE_PICK_TASK where WARE_ID=13583852 and(nvl(PICKED_QTY,0)>0 or LEGACY_SBORKA_PALLET_ID is not null);
 if n!=0 then raise_application_error(-20886,'CASE_TRANSIT_USED_HISTORY_PRESERVE_FORWARD_REPAIR');end if;
 select count(*)into n from RRL_CELLS where CELL='CPT_13583852'and WARE_ID=13583852 and IS_SYSTEM=1 and OTBOR=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;
 if n!=1 then raise_application_error(-20886,'CASE_TRANSIT_ROLLBACK_CONFIGURATION_CHANGED');end if;
 delete from RRL_STOCK_POLICY_GUARD where POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CELL','CPT_13583852')and POLICY_VERSION=1;
 if sql%rowcount!=1 then raise_application_error(-20886,'CASE_TRANSIT_ROLLBACK_POLICY_CHANGED');end if;
 delete from RRL_CELLS where CELL='CPT_13583852';
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'CASE_TRANSIT_ROLLBACK_INVALID');end if;
 update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-case-transit-13583852';
 commit;RRL_STOCK_CONFIG_API.end_change;
exception when others then rollback;RRL_STOCK_CONFIG_API.end_change;raise;end;
/
