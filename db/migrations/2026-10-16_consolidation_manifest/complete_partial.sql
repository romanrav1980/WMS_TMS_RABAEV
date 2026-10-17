@@partial_sources.sql
declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID'and not(OBJECT_NAME='RRL_HU_CONSOL_READ'and OBJECT_TYPE='PACKAGE BODY');if n!=0 then raise_application_error(-20886,'CONSOL_PARTIAL_UNEXPECTED_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%'and not(NAME='RRL_HU_CONSOL_READ'and TYPE='PACKAGE BODY'and LINE=58 and POSITION in(128,19));if n!=0 then raise_application_error(-20886,'CONSOL_PARTIAL_UNEXPECTED_ERRORS');end if;
 select count(*)into n from USER_ERRORS where NAME='RRL_HU_CONSOL_READ'and TYPE='PACKAGE BODY'and LINE=58;if n!=2 then raise_application_error(-20886,'CONSOL_PARTIAL_EXPECTED_SYNTAX_ERROR');end if;
 select(select count(*)from RRL_HU_CONSOL_PLAN)+(select count(*)from RRL_HU_CONSOL_MEMBER)+(select count(*)from RRL_HU_CONSOL_RECEIPT)into n from dual;if n!=0 then raise_application_error(-20886,'CONSOL_PARTIAL_NOT_EMPTY');end if;
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-16-consolidation-manifest';if n!=0 then raise_application_error(-20886,'CONSOL_PARTIAL_LEDGER_EXISTS');end if;
end;
/
@@rrl_hu_consol_read_package_body.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-consolidation-manifest','Expected consolidation metadata and native shipping guard',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
