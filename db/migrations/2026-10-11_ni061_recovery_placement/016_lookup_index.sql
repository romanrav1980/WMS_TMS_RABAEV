declare n number;begin
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_REC_PUT_RECEIPT_IX';
 if n=0 then execute immediate 'create index RRL_IW_REC_PUT_RECEIPT_IX on RRL_IW_RECOVERY_PUT_PLAN(RECOVERY_OPERATION_ID,TASK_ID)';end if;
 dbms_stats.gather_table_stats(user,'RRL_IW_RECOVERY_PUT_PLAN',cascade=>true,no_invalidate=>false);
 dbms_stats.gather_table_stats(user,'RRL_IW_RECOVERY_PLACEMENT',cascade=>true,no_invalidate=>false);
end;
/
