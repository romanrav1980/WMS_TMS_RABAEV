-- Explicit rollback refuses to discard imported master data or supply documents.
declare n number;
begin
 if user!='RABAEV' then raise_application_error(-20801,'RABAEV only'); end if;
 select (select count(*) from RRL_SAP_ARTICLE_META)+(select count(*) from RRL_SAP_SUPPLY_ORDER)
 +(select count(*) from RRL_SAP_IDOC_INBOX where RESULT_JSON is not null) into n from dual;
 if n>0 then raise_application_error(-20802,'Imported facts exist: reconcile/export before rollback'); end if;
 execute immediate 'drop table RRL_SAP_SUPPLY_MESSAGE';
 execute immediate 'drop table RRL_SAP_SUPPLY_LINE';
 execute immediate 'drop table RRL_SAP_SUPPLY_ORDER';
 execute immediate 'drop table RRL_SAP_ARTICLE_META';
 execute immediate 'alter table RRL_SAP_IDOC_INBOX drop column LAST_ERROR';
 execute immediate 'alter table RRL_SAP_IDOC_INBOX drop column RESULT_JSON';
 update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-07-002-ni01-sap-supply';
 commit;
end;
/
