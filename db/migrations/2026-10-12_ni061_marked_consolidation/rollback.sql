declare n number;begin select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='STORE_RECEIPT'and STATE='APPLIED'and json_value(RESOLVED_PLAN_JSON,'$.domain.snapshot.leaf_count'returning number)>1 and json_value(RESOLVED_PLAN_JSON,'$.domain.requires_marked_recipient_flow')='true';if n>0 then raise_application_error(-20899,'MARKED_CONSOLIDATED_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before_units.sql
@@000_before_store.sql
@@000_before_ship.sql
@@004_recompile.sql
