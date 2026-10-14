declare n number;begin
 select count(*)into n from RRL_WAREHOUSE_TASK where FINISHED_AT_INSTANT is not null;
 if n>0 then raise_application_error(-20886,'TASK_FINISH_CLOCK_FACTS_REMAIN_NO_DROP');end if;
end;
/
drop trigger RRL_WTASK_FINISH_TIME_GUARD;
/
alter table RRL_WAREHOUSE_TASK drop column FINISHED_AT_INSTANT;
/
@003_recompile.sql
