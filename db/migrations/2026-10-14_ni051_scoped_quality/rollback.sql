-- Restore code only; retain configuration history and posted exemption audit.
@@saved/RRL_STOCK_QC_POLICY_PACKAGE_BODY.sql
@@saved/RRL_STOCK_QC_GATE_PACKAGE_BODY.sql
@@saved/RRL_STOCK_SHIPPING_CORE_PACKAGE_BODY.sql
@@saved/RRL_STOCK_PALLET_QC_CMD_PACKAGE_BODY.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-1447-ni051-scoped-quality';
commit;
/

-- RRL_QC_EXEMPT_DOCUMENT_IX is retained as an additive audit lookup index.
