merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-275-shipping-register-index'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Bounded dated ST shipping register and declared cell occupancy',sysdate,user,
'db/migrations/2026-10-11_ni072_shipping_register/001_index.sql','db/migrations/2026-10-11_ni072_shipping_register/rollback.sql','APPLIED',
'ExistingST cursor/currentload vslogicalproof/sameDayReview snapshot/no falseempty. Member737-14.507ms26buffers/cell3782-27.464ms48buffers afterboundedSQL/sparse178reuse/WARE-STDATE-ID indexVALID. Ownpositivecell tempconfig rollback/P20H20/noqty; completearea unknown.');
commit;
