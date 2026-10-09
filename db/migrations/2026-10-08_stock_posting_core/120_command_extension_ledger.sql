declare n number;v varchar2(100);begin
 select count(*) into n from USER_OBJECTS where STATUS!='VALID' and (OBJECT_NAME like 'RRL_STOCK_%' or OBJECT_NAME in('RRL_PICKING_API','RRL_PICK_WAVE_API','RRL_PICK_WAVE_META','RRL_MES_PRODUCTION_API'));
 if n>0 then raise_application_error(-20808,'CURRENT_COMMAND_PACKAGES_INVALID');end if;
 select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;if v!='PREPARED' then raise_application_error(-20808,'DORMANT_LEDGER_REQUIRES_PREPARED');end if;
 select SETTING_VALUE into v from RRL_SYSTEM_SETTINGS where SETTING_KEY='STOCK_LEGACY_TRIGGER_ENABLED';if v!='0' then raise_application_error(-20808,'COMPATIBILITY_MUST_BE_OFF');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-037-native-mes-batch' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Native MES movement batch through fixed command; code installed, no cutover',sysdate,user,'101_native_mes_apply.sql','101_native_mes_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-038-inventory-lot-command' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Lot-specific measured inventory command and exact base policy',sysdate,user,'103_inventory_count_apply.sql','103_inventory_count_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-039-wave-command-lifecycle' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Wave HARD, existing projections, release/cancel and own replenishment coverage',sysdate,user,'108_wave_launch_apply.sql','108_wave_launch_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-040-shipment-owned-stock' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Existing fulfillment binds own picked HARD to legacy pallet shipment; regulatory check',sysdate,user,'112_shipping_owned_stock_apply.sql','112_shipping_owned_stock_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-041-oracle-json-binds' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Oracle 19c static SQL uses typed local JSON binds; physical acceptance outstanding',sysdate,user,'114_oracle_json_bindings_apply.sql','114_oracle_json_bindings_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-042-plan-cancel-base-quantity' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Native plan cancel, base quantity planning and reservation/task closure through 119',sysdate,user,'117_picking_plan_cancel_apply.sql','117_picking_plan_cancel_rollback.sql','APPLIED');
commit;
