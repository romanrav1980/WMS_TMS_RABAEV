prompt SAP adapter metadata for existing ORDERS/SBORKA/TMS; no new assignment engine
declare n number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 select count(*) into n from user_tab_columns where table_name='RRL_SAP_STORE_ORDER' and column_name='PREPARATION_JSON';
 if n=0 then
  execute immediate 'alter table RRL_SAP_STORE_ORDER add (PREPARATION_HASH varchar2(64),PREPARATION_JSON clob,PREPARED_AT timestamp)';
  execute immediate 'alter table RRL_SAP_STORE_ORDER add constraint RRL_SAP_STORE_PREP_JSON check(PREPARATION_JSON is json)';
 end if;
 execute immediate 'alter table RRL_CUSTOMER_ORDER_FULFILLMENT drop constraint RRL_CUST_ORDER_FULF_CHK1';
 execute immediate q'[alter table RRL_CUSTOMER_ORDER_FULFILLMENT add constraint RRL_CUST_ORDER_FULF_CHK1 check(STATUS in('LEGACY_FACT','PICKED','SHIPPED','CANCELLED','PLANNED'))]';
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-07-009-ni02-legacy-st-adapter' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'SAP adapter to existing ST writers, planned fulfillment and durable result',sysdate,user,'009_apply.sql','009_rollback.sql','APPLIED');
commit;