prompt NI01 regulatory journal namespace and bounded composition lookup
declare n number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 select count(*) into n from RRL_WMS_RECEIPT_CODE where CANONICAL_CODE is null;
 if n>0 then raise_application_error(-20805,'Backfill canonical receipt identities before enforcing the contract'); end if;
 select count(*) into n from user_tab_columns where table_name='RRL_WMS_RECEIPT_CODE' and column_name='CANONICAL_CODE' and nullable='Y';
 if n>0 then execute immediate 'alter table RRL_WMS_RECEIPT_CODE modify CANONICAL_CODE not null'; end if;
 select count(*) into n from user_tab_columns where table_name='RRL_REG_OPERATION_JOURNAL' and column_name='SYSTEM_CODE' and data_length<40;
 if n>0 then execute immediate 'alter table RRL_REG_OPERATION_JOURNAL modify SYSTEM_CODE varchar2(40)'; end if;
 execute immediate 'alter package RRL_REGULATORY_API compile body';
 select count(*) into n from user_indexes where index_name='RRL_WMS_REC_CODE_PAL_IX';
 if n=0 then execute immediate 'create index RRL_WMS_REC_CODE_PAL_IX on RRL_WMS_RECEIPT_CODE(UID_PALLET,UNIT_ID)'; end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-07-006-ni01-registry-contract' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI01 marking namespace and canonical composition contract',sysdate,user,'006_apply.sql','006_rollback.sql','APPLIED');
commit;
