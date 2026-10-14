merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-252-regulatory-source-warehouse-index'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Regulatory day board source warehouse and matching functional JSON index',sysdate,user,'db/migrations/2026-10-11_ni072_regulatory_scope/apply.sql','db/migrations/2026-10-11_ni072_regulatory_scope/rollback.sql','APPLIED','Existing236-237 sourceWARE51365792 CRPT-EGAIS/currentAPPLIED/foreign403/no qty/ACK inference. Old query180.838ms3/new12.917ms2/explicit index after metadata check. Architecture5740cycles76/JS/protected20-20.');
commit;
