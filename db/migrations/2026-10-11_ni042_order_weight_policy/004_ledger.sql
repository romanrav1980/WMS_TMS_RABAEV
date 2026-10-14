merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-191-order-weight-policy'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Separate exact SKU order weight tolerance default15 and current original order SKU preview',sysdate,user,
'db/migrations/2026-10-11_ni042_order_weight_policy/apply.sql','db/migrations/2026-10-11_ni042_order_weight_policy/rollback.sql','APPLIED',
'CASE1069 original10/picked9.6 within15 outside2; default/current card history/version/stale409/invalid100.01422/old clients preserve2. Explicit completion/lastbox next; native original requested_base_quantity, not unallocated pool quantity.');
commit;
