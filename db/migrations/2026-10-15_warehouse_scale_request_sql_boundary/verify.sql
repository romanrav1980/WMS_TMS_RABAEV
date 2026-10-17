select NAME,TYPE,LINE,POSITION,TEXT from USER_ERRORS where NAME='RRL_WH_WEIGH_REQUEST_API';
select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID';
select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID in('2026-10-15-warehouse-scale-requests','2026-10-15-warehouse-scale-request-sql-boundary');
