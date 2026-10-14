begin execute immediate 'create index RRL_CASE_LINE_CELL_TASK_IX on RRL_CASE_PICK_LINE(CELL_CODE,CASE_PICK_TASK_ID)';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_WH_TASK_FROM_CELL_IX on RRL_WAREHOUSE_TASK(FROM_CELL,STATUS)';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_WH_TASK_TO_CELL_IX on RRL_WAREHOUSE_TASK(TO_CELL,STATUS)';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_REPL_TARGET_CELL_IX on RRL_PICK_WAVE_REPLENISH_TASK(TARGET_CELL_CODE,STATUS)';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
