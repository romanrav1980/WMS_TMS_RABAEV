select object_name,object_type,status from user_objects where (object_name like 'RRL_ACCESS%' or object_name like 'RRL_KNOWLEDGE%' or object_name='RRL_PLATFORM_COMMAND') order by object_name;
select name,type,line,text from user_errors where name in('RRL_ACCESS_API','RRL_KNOWLEDGE_API') order by name,sequence;
select count(*) INVALID_COUNT from user_objects where status='INVALID';
select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-14-scoped-access-knowledge';
select count(*) UNEXPECTED_ASSIGNMENTS from RRL_ACCESS_ASSIGNMENT;
