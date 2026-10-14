declare n number;fk_count number;pk_name varchar2(128);begin
 for item in(select 'RRL_INTERWARE_SHORTAGE_UNIT'TAB,'FACT_OPERATION_ID'EVENT_COL,'RRL_IW_LOSS_EVENT_UNIT_PK'PK_NAME,'RRL_IW_LOSS_EVENT_UNIT_UK'IX_NAME from dual
 union all select 'RRL_INTERWARE_RECOVERY_UNIT','RECOVERY_OPERATION_ID','RRL_IW_REC_EVENT_UNIT_PK','RRL_IW_REC_EVENT_UNIT_UK'from dual)loop
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME=item.TAB and CONSTRAINT_NAME=item.PK_NAME and CONSTRAINT_TYPE='P';
 if n=0 then
  select CONSTRAINT_NAME into pk_name from USER_CONSTRAINTS where TABLE_NAME=item.TAB and CONSTRAINT_TYPE='P';
  select count(*)into fk_count from USER_CONSTRAINTS where R_CONSTRAINT_NAME=pk_name;
  if fk_count>0 then raise_application_error(-20886,'EVENT_UNIT_PK_REFERENCED_REQUIRES_EXPLICIT_MIGRATION');end if;
  select count(*)into n from USER_INDEXES where INDEX_NAME=item.IX_NAME;
  if n=0 then execute immediate 'create unique index '||item.IX_NAME||' on '||item.TAB||'(PHYSICAL_UNIT_KEY,'||item.EVENT_COL||')';end if;
  execute immediate 'alter table '||item.TAB||' drop primary key';
  execute immediate 'alter table '||item.TAB||' add constraint '||item.PK_NAME||' primary key(PHYSICAL_UNIT_KEY,'||item.EVENT_COL||') using index '||item.IX_NAME;
 end if;
 end loop;
end;
/
