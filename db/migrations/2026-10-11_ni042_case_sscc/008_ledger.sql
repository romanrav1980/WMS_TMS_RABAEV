merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-203-case-logistic-sscc'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Original CASE SSCC issuance and attached-label admission',sysdate,user,
'db/migrations/2026-10-11_ni042_case_sscc/apply.sql','db/migrations/2026-10-11_ni042_case_sscc/rollback.sql','APPLIED',
'Own QPB20356E93BB1 type8 CASE6: 18digit SSCC 090000000000000025 synthetic test prefix; native metadata rollback/original CP history/replay/conflict/print GS1 SVG ZPL/confirm/direct history guard; existing CASE6 QC/source14/native cleanup. Small final-required containers label before pick. No government ACK or GS1 ownership claim.');
commit;
