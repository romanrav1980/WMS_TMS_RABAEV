select object_name,status from user_objects where object_name in('RRL_TRANSPORT_PLAN_RULES','RRL_TRANSPORT_EDIT_API');
select name,type,line,text from user_errors where name in('RRL_TRANSPORT_PLAN_RULES','RRL_TRANSPORT_EDIT_API');
select count(*) INVALID_COUNT from user_objects where status='INVALID';
select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-transport-scoped-edit';
