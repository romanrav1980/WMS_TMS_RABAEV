declare n number;begin
 select count(*)into n from RRL_TT_UNLOAD_FACT u join RRL_STOCK_OPERATION o on o.OPERATION_ID=u.OPERATION_ID where json_exists(o.RESOLVED_PLAN_JSON,'$.domain.members[*]?(@.physical_uid != null)');
 if n>0 then raise_application_error(-20863,'UNLOAD_FULLPAL_HISTORY_FORWARD_REPAIR_REQUIRED');end if;
end;
/
@@000_before_unload.sql
@@000_before_fulfillment.sql
