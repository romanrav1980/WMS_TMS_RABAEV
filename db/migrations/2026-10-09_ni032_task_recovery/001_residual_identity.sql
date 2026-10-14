-- Preserve one root per legacy identity and one residual per parent.
-- Install the new protection before dropping the former, overly broad index.
declare n number;begin
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_WAREHOUSE_TASK_U2';
 if n=0 then execute immediate 'create unique index RRL_WAREHOUSE_TASK_U2 on RRL_WAREHOUSE_TASK(TASK_SOURCE,nvl(SOURCE_TASK_ID,-1),nvl(SOURCE_MOVEMENT_ID,-1),TASK_TYPE,nvl(PARENT_TASK_ID,-1))';end if;
 select count(*) into n from USER_IND_COLUMNS where INDEX_NAME='RRL_WAREHOUSE_TASK_U2';
 if n!=5 then raise_application_error(-20808,'RESIDUAL_IDENTITY_INDEX_DRIFT');end if;
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_WAREHOUSE_TASK_U1';
 if n=1 then execute immediate 'drop index RRL_WAREHOUSE_TASK_U1';end if;
end;
/
