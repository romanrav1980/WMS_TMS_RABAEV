declare references_count number;
begin
 for x in(select c.CONSTRAINT_NAME from USER_CONSTRAINTS c join USER_CONS_COLUMNS col
 on col.CONSTRAINT_NAME=c.CONSTRAINT_NAME and col.TABLE_NAME=c.TABLE_NAME
 where c.TABLE_NAME='RRL_LOGISTICS_RATE_HISTORY'and c.CONSTRAINT_TYPE='U'
 group by c.CONSTRAINT_NAME having listagg(col.COLUMN_NAME,',')within group(order by col.COLUMN_NAME)='EFFECTIVE_FROM,RATE_KEY')loop
 select count(*)into references_count from ALL_CONSTRAINTS where CONSTRAINT_TYPE='R'and R_OWNER=user and R_CONSTRAINT_NAME=x.CONSTRAINT_NAME;
 if references_count!=0 then raise_application_error(-20899,'RATE_PERIOD_UNIQUE_HAS_DEPENDENT_FOREIGN_KEYS');end if;
 execute immediate 'alter table RRL_LOGISTICS_RATE_HISTORY drop constraint '||dbms_assert.simple_sql_name(x.CONSTRAINT_NAME);
 end loop;
end;
/
begin execute immediate 'create index RRL_LOG_RATE_DATE_VER_IX on RRL_LOGISTICS_RATE_HISTORY(RATE_KEY,EFFECTIVE_FROM desc,VERSION_NO desc)';
exception when others then if sqlcode not in(-955,-1408)then raise;end if;end;
/
