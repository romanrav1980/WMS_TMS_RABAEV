declare n number;
begin
 if user!='RABAEV' then raise_application_error(-20801,'RABAEV only'); end if;
 select count(*) into n from RRL_REG_OPERATION_JOURNAL where lengthb(SYSTEM_CODE)>20;
 if n>0 then raise_application_error(-20802,'Long regulatory namespaces exist; retain widened contract'); end if;
 execute immediate 'alter table RRL_REG_OPERATION_JOURNAL modify SYSTEM_CODE varchar2(20)';
 execute immediate 'alter table RRL_WMS_RECEIPT_CODE modify CANONICAL_CODE null';
 execute immediate 'drop index RRL_WMS_REC_CODE_PAL_IX';
 update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-07-006-ni01-registry-contract';
 commit;
end;
/
