-- Do not remove protection or facts if residual history prevents the old uniqueness.
declare n number;begin
 select count(*) into n from(
  select TASK_SOURCE,nvl(SOURCE_TASK_ID,-1),nvl(SOURCE_MOVEMENT_ID,-1),TASK_TYPE
   from RRL_WAREHOUSE_TASK
  group by TASK_SOURCE,nvl(SOURCE_TASK_ID,-1),nvl(SOURCE_MOVEMENT_ID,-1),TASK_TYPE
  having count(*)>1);
 if n>0 then raise_application_error(-20808,'RESIDUAL_HISTORY_PREVENTS_OLD_INDEX_ROLLBACK: retain current index and facts');end if;
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_WAREHOUSE_TASK_U1';
 if n=0 then execute immediate 'create unique index RRL_WAREHOUSE_TASK_U1 on RRL_WAREHOUSE_TASK(TASK_SOURCE,nvl(SOURCE_TASK_ID,-1),nvl(SOURCE_MOVEMENT_ID,-1),TASK_TYPE)';end if;
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_WAREHOUSE_TASK_U2';
 if n=1 then execute immediate 'drop index RRL_WAREHOUSE_TASK_U2';end if;
end;
/
