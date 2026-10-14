merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-289-reuse-approval-source'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Early existing return reuse source and readonly preview',sysdate,user,'db/migrations/2026-10-11_ni062_reuse_approval/001_reuse_helper.sql','db/migrations/2026-10-11_ni062_reuse_approval/rollback.sql','APPLIED','Nativecompile/fresh checkedSAPbatch/fullBOX/UOMexpiry; currentreadonlypreview. Actuallegacybatchnegative/BOX24positive-source available0/BOX12fractional/gateway403/HTTP noqty. FreshphysicalmarkedREUSE independent notclaimed.');
commit;
