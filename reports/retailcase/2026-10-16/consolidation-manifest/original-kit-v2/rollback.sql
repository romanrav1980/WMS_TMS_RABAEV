@@after_sources.sql
declare n number;begin
 select(select count(*)from RRL_HU_CONSOL_PLAN)+(select count(*)from RRL_HU_CONSOL_MEMBER)+(select count(*)from RRL_HU_CONSOL_RECEIPT)into n from dual;
 if n!=0 then raise_application_error(-20886,'CONSOLIDATION_RETAINED_HISTORY_FORWARD_RECOVERY_REQUIRED');end if;
end;
/
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

@@restore_rrl_stock_hu_ship_cmd_package_body.sql
drop trigger RRL_HU_CONSOL_PLAN_GUARD;
drop trigger RRL_HU_CONSOL_MEMBER_GUARD;
drop trigger RRL_HU_CONSOL_RECEIPT_GUARD;
drop package RRL_HU_CONSOL_API;
drop package RRL_HU_CONSOL_READ;
drop table RRL_HU_CONSOL_RECEIPT;
drop table RRL_HU_CONSOL_MEMBER;
drop table RRL_HU_CONSOL_PLAN;
@@compile_dependents.sql
@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-16-consolidation-manifest';
commit;
