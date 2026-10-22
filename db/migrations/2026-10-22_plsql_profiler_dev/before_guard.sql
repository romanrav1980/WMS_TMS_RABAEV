declare n number;begin
 if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('PLSQL_PROFILER_RUNS','PLSQL_PROFILER_UNITS','PLSQL_PROFILER_DATA','PLSQL_PROFILER_RUNNUMBER');
 if n<>0 then raise_application_error(-20999,'PROFILER_OBJECTS_EXIST_DO_NOT_REPLACE');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BASELINE');end if;
end;
/
