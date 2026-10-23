whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
end;
/
-- Recorded losses are working history: once any exists the rollback refuses instead of deleting it.
declare n number;begin select count(*)into n from RRL_INVENTORY_LOSS_UNIT;if n<>0 then raise_application_error(-20999,'INVENTORY_LOSS_HISTORY_PRESENT');end if;end;
/
@@before_unit_core_spec.sql
@@before_unit_core_body.sql
@@before_inventory_cmd_body.sql
drop table RRL_INVENTORY_FOUND_UNIT purge;
drop table RRL_INVENTORY_LOSS_UNIT purge;
begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-inventory-found-units' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Inventory loss journal and restoration of the same marked units via INVENTORY_COUNT',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
