declare n number;begin
 RRL_STOCK_METADATA_TX.begin_change('admin','warehouse_task_edit');
 select count(*) into n from RRL_WAREHOUSE_TASK t join RRL_RESOURCE r on r.RESOURCE_ID=t.RESOURCE_ID
  where t.TASK_TYPE='PUTAWAY' and t.STATUS in('ASSIGNED','IN_PROGRESS') and r.RESOURCE_TYPE in('REACHTRUCK','FORKLIFT');
 if n>0 then raise_application_error(-20808,'PUTAWAY_CAPABILITY_IN_USE');end if;
 update RRL_RESOURCE_TYPE set DEFAULT_TASK_TYPES=trim(both ',' from replace(','||DEFAULT_TASK_TYPES||',',',PUTAWAY,',',')),UPDATED_AT=systimestamp
  where RESOURCE_TYPE in('REACHTRUCK','FORKLIFT');
 RRL_STOCK_METADATA_TX.end_change;
exception when others then RRL_STOCK_METADATA_TX.end_change;raise;
end;
/
@@../2026-10-09_ni032_case_resources/002_warehouse_policy.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-017-putaway-capability';
commit;
/
