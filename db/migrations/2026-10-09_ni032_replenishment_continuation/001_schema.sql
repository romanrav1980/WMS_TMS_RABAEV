declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PICK_WAVE_REPLENISH_TASK' and COLUMN_NAME='PARENT_REPLENISH_TASK_ID';
 if n=0 then execute immediate 'alter table RRL_PICK_WAVE_REPLENISH_TASK add PARENT_REPLENISH_TASK_ID number';end if;
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_REPL_CONT_PARENT_U1';
 if n=0 then execute immediate 'create unique index RRL_REPL_CONT_PARENT_U1 on RRL_PICK_WAVE_REPLENISH_TASK(PARENT_REPLENISH_TASK_ID)';end if;
end;
/
