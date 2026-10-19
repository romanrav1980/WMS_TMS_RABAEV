whenever sqlerror exit failure rollback
begin
 dbms_stats.delete_table_stats(user,'RRL_TRADE_STOCK_ATTR',cascade_indexes=>true,no_invalidate=>false);
 dbms_stats.delete_table_stats(user,'RRL_TRADE_BUYOUT',cascade_indexes=>true,no_invalidate=>false);
 dbms_stats.delete_table_stats(user,'RRL_TRADE_BUYOUT_UNIT',cascade_indexes=>true,no_invalidate=>false);
 dbms_stats.delete_table_stats(user,'RRL_TRADE_OWNER_GRANT',cascade_indexes=>true,no_invalidate=>false);
 dbms_stats.delete_table_stats(user,'RRL_TRADE_DOCUMENT',cascade_indexes=>true,no_invalidate=>false);
 dbms_stats.delete_table_stats(user,'RRL_TRADE_ORDER_LINE',cascade_indexes=>true,no_invalidate=>false);
 dbms_stats.import_table_stats(user,'RRL_WMS_RECEIPT_UNIT',stattab=>'RRL_TC_STATS_20261019',statid=>'BEFORE_20261019',cascade=>true,no_invalidate=>false);
end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-19-tradecase-statistics';
commit;
