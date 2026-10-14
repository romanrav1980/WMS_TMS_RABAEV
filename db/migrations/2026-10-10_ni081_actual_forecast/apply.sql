@@001_schema.sql
@@002_source_rules.sql
@@003_projector.sql
@@004_guards.sql
declare
begin
 for t in(select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_TT_HU_LOAD_FACT')loop execute immediate 'alter trigger '||t.TRIGGER_NAME||' compile';end loop;
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_FORECAST_SOURCE_RULES','RRL_FORECAST_PROJECTOR','RRL_FORECAST_LOAD_GUARD','RRL_FORECAST_LEAF_GUARD','RRL_FORECAST_ORIGIN_GUARD','RRL_FORECAST_DAY_GUARD','RRL_FORECAST_SKU_DAY_GUARD')and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'FORECAST133_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-133-native-execution-forecast-projection' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Async immutable departed load/CASE origin projection and daily quantity counters; no warehouse stock writes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
