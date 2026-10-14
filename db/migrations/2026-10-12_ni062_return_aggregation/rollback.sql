declare n number;begin
 select count(*)into n from RRL_STOCK_OPERATION where STATE='APPLIED'and COMMAND_TYPE in('STORE_RETURN_HANDOVER','STORE_RETURN_PICKUP','STORE_RETURN_RECEIVE')
 and json_exists(CANONICAL_REQUEST,'$.metadata.aggregation_scans[*]');
 if n!=0 then raise_application_error(-20886,'RETURN_AGGREGATION_FACTS_REQUIRE_FORWARD_REPAIR');end if;end;
/
@@000_before_rrl_store_return_unit_core_package_body.sql
@@000_before_rrl_iw_agg_scan_package.sql
alter package RRL_IW_AGG_SCAN compile body;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-619-return-aggregation-custody';
