declare n number;
 procedure add_column(p_name varchar2,p_type varchar2) is begin
  select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PICK_WAVE_REPLENISH_TASK' and COLUMN_NAME=p_name;
  if n=0 then execute immediate 'alter table RRL_PICK_WAVE_REPLENISH_TASK add '||p_name||' '||p_type;end if;
 end;
begin
 add_column('MINIMAX_CYCLE_ID','number');
 add_column('MINIMAX_TARGET_BASE','number');
 add_column('MINIMAX_FINISHED_AT','timestamp');
end;
/
