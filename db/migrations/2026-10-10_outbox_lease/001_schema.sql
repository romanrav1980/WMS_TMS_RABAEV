declare n number;
 procedure add_col(p_table varchar2,p_column varchar2,p_ddl varchar2)is begin
  select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME=p_table and COLUMN_NAME=p_column;
  if n=0 then execute immediate 'alter table '||p_table||' add ('||p_ddl||')';end if;
 end;
begin
 add_col('RRL_EVENT_OUTBOX','CLAIM_VERSION','CLAIM_VERSION number(19) default 0 not null');
 add_col('RRL_EVENT_OUTBOX','LEASE_UNTIL','LEASE_UNTIL timestamp with time zone');
 add_col('RRL_ADAPTER_REQUEST_LOG','CLAIM_VERSION','CLAIM_VERSION number(19) default 0 not null');
 add_col('RRL_ADAPTER_REQUEST_LOG','CLAIM_WORKER','CLAIM_WORKER varchar2(100)');
 add_col('RRL_ADAPTER_REQUEST_LOG','FINISH_HASH','FINISH_HASH varchar2(64)');
 add_col('RRL_ADAPTER_REQUEST_LOG','RESPONSE_AT_TZ','RESPONSE_AT_TZ timestamp with time zone');
end;
/
