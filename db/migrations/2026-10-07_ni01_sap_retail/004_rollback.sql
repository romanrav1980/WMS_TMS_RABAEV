declare n number;
begin
 if user!='RABAEV' then raise_application_error(-20801,'RABAEV only'); end if;
 select (select count(*) from RRL_WMS_RECEIPT_UNIT)+(select count(*) from RRL_SAP_TRACE_AGG) into n from dual;
 if n>0 then raise_application_error(-20802,'Marking/source facts exist: export and reconcile before rollback'); end if;
 execute immediate 'drop table RRL_WMS_RECEIPT_AGG';
 execute immediate 'drop table RRL_WMS_RECEIPT_CODE';
 execute immediate 'drop table RRL_WMS_RECEIPT_UNIT';
 execute immediate 'drop table RRL_SAP_TRACE_AGG';
 update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-07-004-ni01-receipt-marking';
 commit;
end;
/
