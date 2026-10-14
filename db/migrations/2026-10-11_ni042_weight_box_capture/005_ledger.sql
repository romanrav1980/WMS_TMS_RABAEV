merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-179-weight-box-physical-capture'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Serialized weighted boxes in existing physical unit registry, exact GS1 net KG, independent WMS policy flag',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_box_capture/apply.sql','db/migrations/2026-10-11_ni042_weight_box_capture/rollback.sql','APPLIED',
'Own QW1794B408748 born P9.8KG/H0/unit1/codes0; exact replay, duplicate and mass mismatch refused without orphan lot; native count cleanup; original135 P20H20 preserved; changed packages VALID; SAP/CASE scanner remain next');
commit;
