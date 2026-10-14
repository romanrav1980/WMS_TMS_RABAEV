-- Refuse restoring the incompatible historical key after multiple SAP putaway facts.
declare n number;begin
 select count(*)into n from(select SOURCE_TASK_ID,SOURCE_MOVEMENT_ID,TASK_TYPE,PARENT_TASK_ID from RRL_WAREHOUSE_TASK
 group by TASK_SOURCE,SOURCE_TASK_ID,SOURCE_MOVEMENT_ID,TASK_TYPE,PARENT_TASK_ID having count(*)>1);
 if n>0 then raise_application_error(-20886,'OLD_TASK_IDENTITY_CANNOT_REPRESENT_CURRENT_HISTORY');end if;
end;
/
drop index RRL_WAREHOUSE_TASK_U2;
@@000_before_index.sql
