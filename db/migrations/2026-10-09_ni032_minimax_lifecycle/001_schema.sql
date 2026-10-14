-- Operational planning intent on the existing replenishment row; no quantity projection.
declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PICK_WAVE_REPLENISH_TASK' and COLUMN_NAME='RESERVE_OPERATION_ID';
 if n=0 then execute immediate 'alter table RRL_PICK_WAVE_REPLENISH_TASK add RESERVE_OPERATION_ID varchar2(100)';end if;
end;
/
