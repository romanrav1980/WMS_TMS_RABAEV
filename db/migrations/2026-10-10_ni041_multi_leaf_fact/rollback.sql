-- Rollback never deletes real movement history. Refuse if multi-leaf task facts already exist.
declare n number;begin
 select count(*) into n from(select TASK_ID from RRL_WAREHOUSE_TASK_STOCK_MOVE group by TASK_ID having count(*)>1);
 if n>0 then raise_application_error(-20886,'MULTI_LEAF_FACT_HISTORY_REQUIRES_COMPOSITE_KEY');end if;
 execute immediate 'alter table RRL_WAREHOUSE_TASK_STOCK_MOVE drop constraint RRL_WH_TASK_STOCK_MOVE_U1';
 execute immediate 'alter table RRL_WAREHOUSE_TASK_STOCK_MOVE add constraint RRL_WH_TASK_STOCK_MOVE_U1 unique(TASK_ID)';
end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-070-hu-multi-leaf-fact';
commit;
/
