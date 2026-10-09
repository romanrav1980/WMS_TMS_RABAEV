prompt NI01 marking physical units retain base quantity independently of profile count
declare n number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 select count(*) into n from user_tab_columns where table_name='RRL_WMS_RECEIPT_UNIT' and column_name='BASE_QTY';
 if n=0 then execute immediate 'alter table RRL_WMS_RECEIPT_UNIT add BASE_QTY number default 1 not null'; end if;
 select count(*) into n from user_constraints where constraint_name='RRL_WMS_REC_UNIT_QTY_CK';
 if n=0 then execute immediate 'alter table RRL_WMS_RECEIPT_UNIT add constraint RRL_WMS_REC_UNIT_QTY_CK check(BASE_QTY>0)'; end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-07-007-ni01-unit-quantity' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI01 marked physical quantity separate from unit identity and marking profiles',sysdate,user,'007_apply.sql','007_rollback.sql','APPLIED');
commit;
