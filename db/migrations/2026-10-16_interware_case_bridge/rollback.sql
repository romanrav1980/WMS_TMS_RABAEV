@@after_sources.sql
declare n number;begin select count(*)into n from RRL_IW_CASE_CARRIER;if n!=0 then raise_application_error(-20886,'CASE_BRIDGE_ROLLBACK_RETAINED_HISTORY');end if;select count(*)into n from(select 1 from RRL_IW_GROUP_RECEIPT_LINE group by OPERATION_ID,ST_ID having count(*)>1);if n!=0 then raise_application_error(-20886,'CASE_BRIDGE_ROLLBACK_MULTI_LEAF_HISTORY');end if;end;
/
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

@@restore_rrl_iw_group_archive_package_body.sql
@@restore_rrl_iw_group_rec_package_body.sql
@@restore_rrl_iw_hu_rec_core_package_body.sql
@@restore_rrl_stock_hu_read_package_body.sql
drop trigger RRL_IW_CASE_CARRIER_GUARD;
@@restore_rrl_hu_container_guard_trigger.sql
drop package RRL_IW_CASE_BRIDGE;
drop table RRL_IW_CASE_CARRIER;
drop index RRL_IW_GREC_SOURCE_ST_IX;
alter table RRL_IW_GROUP_RECEIPT_LINE add constraint RRL_IW_GROUP_REC_ST_UQ unique(OPERATION_ID,ST_ID);
@@compile_dependents.sql
@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-16-interware-case-bridge';
commit;
