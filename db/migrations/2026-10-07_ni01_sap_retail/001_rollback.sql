-- Explicit rollback only after exporting retained facts.
declare n number;
begin
 if user!='RABAEV' then raise_application_error(-20801,'RABAEV only'); end if;
 select(select count(*) from RRL_SAP_IDOC_INBOX)+(select count(*) from RRL_SKU_RECEIPT_POLICY_LOG) into n from dual;
 if n>0 then raise_application_error(-20802,'Export IDocs/policy history before rollback'); end if;
 execute immediate 'drop table RRL_SKU_RECEIPT_PROFILE';
 execute immediate 'drop table RRL_SKU_RECEIPT_POLICY_LOG';
 execute immediate 'drop table RRL_SKU_RECEIPT_POLICY';
 execute immediate 'drop table RRL_SAP_IDOC_INBOX';
 update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-07-001-ni01-sap-retail';
 commit;
end;
/