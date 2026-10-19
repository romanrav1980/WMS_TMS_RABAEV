whenever sqlerror exit failure rollback
-- Preserve original receipt statistics. New TRADE tables had no statistics (see evidence).
declare n number;begin
 select count(*)into n from user_tables where TABLE_NAME='RRL_TC_STATS_20261019';
 if n=0 then
  select count(*)into n from user_tab_statistics where partition_name is null and LAST_ANALYZED is not null
   and TABLE_NAME in('RRL_TRADE_STOCK_ATTR','RRL_TRADE_BUYOUT','RRL_TRADE_BUYOUT_UNIT','RRL_TRADE_OWNER_GRANT','RRL_TRADE_DOCUMENT','RRL_TRADE_ORDER_LINE');
  if n<>0 then raise_application_error(-20999,'TRADE_STATISTICS_BASELINE_CHANGED');end if;
  dbms_stats.create_stat_table(user,'RRL_TC_STATS_20261019');
  dbms_stats.export_table_stats(user,'RRL_WMS_RECEIPT_UNIT',stattab=>'RRL_TC_STATS_20261019',statid=>'BEFORE_20261019',cascade=>true);
 end if;
end;
/
begin
 dbms_stats.gather_table_stats(user,'RRL_TRADE_STOCK_ATTR',estimate_percent=>100,cascade=>true,no_invalidate=>false);
 dbms_stats.gather_table_stats(user,'RRL_TRADE_BUYOUT',estimate_percent=>100,cascade=>true,no_invalidate=>false);
 dbms_stats.gather_table_stats(user,'RRL_TRADE_BUYOUT_UNIT',estimate_percent=>100,cascade=>true,no_invalidate=>false);
 dbms_stats.gather_table_stats(user,'RRL_TRADE_OWNER_GRANT',estimate_percent=>100,cascade=>true,no_invalidate=>false);
 dbms_stats.gather_table_stats(user,'RRL_TRADE_DOCUMENT',estimate_percent=>100,cascade=>true,no_invalidate=>false);
 dbms_stats.gather_table_stats(user,'RRL_TRADE_ORDER_LINE',estimate_percent=>100,cascade=>true,no_invalidate=>false);
 dbms_stats.gather_table_stats(user,'RRL_WMS_RECEIPT_UNIT',estimate_percent=>100,cascade=>true,no_invalidate=>false);
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-statistics'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Gather measured TRADECASE plan statistics, preserve original receipt statistics',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
