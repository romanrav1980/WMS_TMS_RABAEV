declare n number;begin
 select count(*)into n from USER_SOURCE where NAME='RRL_STORE_MARK_CORE'and TYPE='PACKAGE BODY'and TEXT like '%STORE_MARK_UNIT_LOT_REQUIRED%';
 if n>0 then raise_application_error(-20899,'RETURN_MATRIX_BRIDGE_REQUIRES_MATCHING_SHARED_CONTRACT_FORWARD_RECOVERY');end if;
end;
/
@@000_before_core.sql
@@002_recompile.sql
