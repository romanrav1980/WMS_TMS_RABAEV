declare n number;begin
 select count(*)into n from RRL_STOCK_OPERATION o where o.COMMAND_TYPE='LOAD_SHIPMENT'and o.STATE='APPLIED'and json_exists(o.RESOLVED_PLAN_JSON,'$.domain.source_stock_claims[0]');
 if n>0 then raise_application_error(-20863,'SINGLE_SLOT_LOAD_HISTORY_FORWARD_REPAIR_REQUIRED');end if;
end;
/
@@000_before_rrl_stock_hu_placement_core.sql
@@000_before_rrl_stock_single_load_cmd.sql
@@003_recompile.sql
