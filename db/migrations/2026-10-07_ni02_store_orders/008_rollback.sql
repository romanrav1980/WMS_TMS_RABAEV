prompt NI02 guarded rollback; explicit rollback instruction required
declare n number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 select (select count(*) from RRL_SAP_STORE_ORDER)+(select count(*) from RRL_SAP_STORE_MESSAGE)+(select count(*) from RRL_SAP_STORE_CALENDAR) into n from dual;
 if n>0 then raise_application_error(-20864,'Export/reconcile owned demand and config before rollback'); end if;
end;
/
drop trigger RRL_SAP_STORE_PICK_GUARD;
drop trigger RRL_SAP_STORE_ROW_GUARD;
drop trigger RRL_SAP_STORE_HEAD_GUARD;
drop table RRL_SAP_STORE_MESSAGE;
drop table RRL_SAP_STORE_ORDER;
drop table RRL_SAP_STORE_CALENDAR;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-07-008-ni02-store-orders';
commit;