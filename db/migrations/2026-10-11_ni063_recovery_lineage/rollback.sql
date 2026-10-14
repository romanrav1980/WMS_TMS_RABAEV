declare n number;begin
 select count(*)into n from RRL_TT_UNLOAD_FACT u join RRL_TARE_LOAD_RECOVERY first_link on first_link.LOAD_OPERATION_ID=u.LOAD_OPERATION_ID join RRL_TARE_LOAD_RECOVERY next_link on next_link.ORIGINAL_BOOK_OPERATION_ID=first_link.OPERATION_ID and next_link.LOAD_OPERATION_ID=u.LOAD_OPERATION_ID;
 if n>0 then raise_application_error(-20863,'REPEATED_TARE_UNLOAD_HISTORY_FORWARD_REPAIR_REQUIRED');end if;
end;
/
@@000_before_rrl_stock_unload_cmd.sql
@@000_before_rrl_tare_load_recovery_api.sql
@@003_recompile.sql
