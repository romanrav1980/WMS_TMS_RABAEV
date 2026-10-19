select object_name,object_type from user_objects where status='INVALID'and object_name not like'BIN$%';
select *from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-19-tradecase-mark-confirmation';
