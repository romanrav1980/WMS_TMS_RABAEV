prompt Guarded rollback only; do not delete prepared ST/business facts
declare n number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 select (select count(*) from RRL_SAP_STORE_ORDER where PREPARATION_JSON is not null)+(select count(*) from RRL_CUSTOMER_ORDER_FULFILLMENT where STATUS='PLANNED') into n from dual;
 if n>0 then raise_application_error(-20864,'Reconcile/export prepared demand before rollback'); end if;
 execute immediate 'alter table RRL_SAP_STORE_ORDER drop constraint RRL_SAP_STORE_PREP_JSON';
 execute immediate 'alter table RRL_SAP_STORE_ORDER drop (PREPARATION_HASH,PREPARATION_JSON,PREPARED_AT)';
 execute immediate 'alter table RRL_CUSTOMER_ORDER_FULFILLMENT drop constraint RRL_CUST_ORDER_FULF_CHK1';
 execute immediate q'[alter table RRL_CUSTOMER_ORDER_FULFILLMENT add constraint RRL_CUST_ORDER_FULF_CHK1 check(STATUS in('LEGACY_FACT','PICKED','SHIPPED','CANCELLED'))]';
end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-07-009-ni02-legacy-st-adapter';
commit;