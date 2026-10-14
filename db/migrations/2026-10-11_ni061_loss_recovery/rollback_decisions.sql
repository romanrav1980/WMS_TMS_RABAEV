declare n number;begin
 select count(*)into n from RRL_INTERWARE_RECOVERY_REQUEST;
 if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_RECOVERY_HISTORY');end if;
end;
/
@@000_before_rrl_stock_posting_api_package_body.sql
-- Preserve additive tables for current readers; remove app before empty schema removal.
