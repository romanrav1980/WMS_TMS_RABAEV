declare n number;begin
 select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='ST_PREPARED_ROW_MOVE'and STATE='APPLIED';
 if n>0 then raise_application_error(-20863,'ST_LAYOUT_HISTORY_RETAIN_FORWARD_REPAIR_REQUIRED');end if;
end;
/
@@000_rrl_stock_posting_api.sql
@@000_rrl_update_sborka_pallet_rows2.sql
