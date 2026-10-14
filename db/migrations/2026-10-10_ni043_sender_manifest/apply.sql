@@001_schema.sql
@@002_guards.sql
@@003_metadata.sql
@@004_aggregation_source.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_METADATA_TX','RRL_TRACE_SENDER_MANIFEST_GUARD','RRL_TRACE_SENDER_AGG_GUARD','RRL_TRACE_MANIFEST_USE_GUARD')and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'TRACE124_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-124-non-sap-versioned-sender-manifest' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Immutable source-scoped non-SAP aggregation proof for inventory/MES birth with original raw JSON and current WMS profile versions; no independent unit registry',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
