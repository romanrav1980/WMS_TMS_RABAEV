declare v_name varchar2(128);v_cols varchar2(500);begin
 select c.CONSTRAINT_NAME,listagg(cc.COLUMN_NAME,',')within group(order by cc.POSITION)into v_name,v_cols from USER_CONSTRAINTS c join USER_CONS_COLUMNS cc on cc.CONSTRAINT_NAME=c.CONSTRAINT_NAME where c.TABLE_NAME='RRL_INTERWARE_ONWARD_DISPATCH'and c.CONSTRAINT_TYPE='P'group by c.CONSTRAINT_NAME;
 if v_cols='OPERATION_ID'then
  execute immediate 'alter table RRL_INTERWARE_ONWARD_DISPATCH drop constraint '||dbms_assert.simple_sql_name(v_name);
  execute immediate 'alter table RRL_INTERWARE_ONWARD_DISPATCH add constraint RRL_IW_ONWARD_DISPATCH_PK primary key(OPERATION_ID,ST_ID)';
 elsif v_cols!='OPERATION_ID,ST_ID'then raise_application_error(-20899,'UNEXPECTED_ONWARD_DISPATCH_PRIMARY_KEY');end if;
end;
/
