begin
 dbms_stats.gather_table_stats(user,'RRL_IW_RECOVERY_ST_BIND',cascade=>true,no_invalidate=>false);
 dbms_stats.gather_table_stats(user,'RRL_IW_RECOVERY_DISPATCH',cascade=>true,no_invalidate=>false);
 dbms_stats.gather_table_stats(user,'RRL_INTERWARE_RECOVERY_RECEIPT',cascade=>true,no_invalidate=>false);
 dbms_stats.gather_table_stats(user,'RRL_INTERWARE_RECOVERY_UNIT',cascade=>true,no_invalidate=>false);
end;
/
