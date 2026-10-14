-- FK prerequisites on actual legacy identities. Existing unique indexes are reused by Oracle.
-- RRL_TRANSPORT_TASK had no ID index/constraint; bounded duplicate discovery found none.
declare n number;
 procedure add_key(p_table varchar2,p_name varchar2) is
 begin
  select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME=p_name;
  if n=0 then execute immediate 'alter table '||p_table||' add constraint '||p_name||' unique(ID)';end if;
 end;
begin
 add_key('RRL_TRANSPORT_TASK','RRL_TRANSPORT_TASK_ID_UK');
 add_key('RRL_TR_VEHICLE','RRL_TR_VEHICLE_ID_UK');
 add_key('RRL_SBORKA_PALLETS','RRL_SBORKA_PALLETS_ID_UK');
end;
/
