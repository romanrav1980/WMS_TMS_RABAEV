-- MIGRATION_ID: 2026-10-14-ni081-route-rest-approval
-- Packages validated and native positive approval rolled back on isolated planning-only TT33641.
declare n number;
begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TT_ROUTE_SCHEDULE','RRL_TT_TIME_API')and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'NI081_ROUTE_PACKAGES_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-ni081-route-rest-approval' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Native route rest schedule shared preview/final approval V6; project planning policy; no stock changes',sysdate,user,'001_route_schedule.sql + 002_time_approval.sql','rollback.sql','APPLIED');
commit;
/
