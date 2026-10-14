declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PICK_WAVE_REPLENISH_TASK' and COLUMN_NAME='DEMAND_BASE_QTY';
 if n=0 then execute immediate 'alter table RRL_PICK_WAVE_REPLENISH_TASK add DEMAND_BASE_QTY number';end if;
end;
/
