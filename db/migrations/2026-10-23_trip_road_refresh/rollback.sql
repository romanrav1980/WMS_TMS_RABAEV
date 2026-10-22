whenever sqlerror exit failure rollback
declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*)into n from RRL_TT_ROAD_REFRESH;if n<>0 then raise_application_error(-20999,'ROAD_REFRESH_HISTORY_PRESENT');end if;
end;
/
drop table RRL_TT_ROAD_REFRESH purge;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user where MIGRATION_ID='2026-10-23-trip-road-refresh';
commit;