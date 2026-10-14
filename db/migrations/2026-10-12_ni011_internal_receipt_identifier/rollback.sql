@000_before_sap_receipt_api.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-686-sap-receipt-internal-uid';
/
