declare key_name varchar2(128);n number;fk_count number;begin
 for item in(select 'RRL_INTERWARE_RECOVERY_REQUEST'TAB,'RRL_IW_REC_REQUEST_LOSS_IX'IX from dual
 union all select 'RRL_INTERWARE_RECOVERY_RECEIPT','RRL_IW_REC_RECEIPT_LOSS_IX'from dual)loop
  select count(*)into n from USER_INDEXES where INDEX_NAME=item.IX;
  if n=0 then execute immediate 'create index '||item.IX||' on '||item.TAB||'(LOSS_OPERATION_ID,OPERATION_ID)';end if;
  for old_key in(select c.CONSTRAINT_NAME from USER_CONSTRAINTS c join USER_CONS_COLUMNS col on col.CONSTRAINT_NAME=c.CONSTRAINT_NAME
   where c.TABLE_NAME=item.TAB and c.CONSTRAINT_TYPE='U'and col.COLUMN_NAME='LOSS_OPERATION_ID'
   and(select count(*)from USER_CONS_COLUMNS same_constraint where same_constraint.CONSTRAINT_NAME=c.CONSTRAINT_NAME)=1)loop
   select count(*)into fk_count from USER_CONSTRAINTS where R_CONSTRAINT_NAME=old_key.CONSTRAINT_NAME;
   if fk_count>0 then raise_application_error(-20886,'RECOVERY_LOSS_UNIQUE_REFERENCED_REQUIRES_EXPLICIT_MIGRATION');end if;
   execute immediate 'alter table '||item.TAB||' drop constraint '||dbms_assert.simple_sql_name(old_key.CONSTRAINT_NAME);
  end loop;
 end loop;
end;
/
