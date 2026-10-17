create or replace trigger RRL_WTASK_IDENTITY_GUARD before delete or update of TASK_ID on RRL_WAREHOUSE_TASK for each row begin
 if deleting then raise_application_error(-20863,'WTASK_IDENTITY_HISTORY_NO_DELETE');end if;
 if :new.TASK_ID is null or :new.TASK_ID!=:old.TASK_ID then raise_application_error(-20863,'WTASK_IDENTITY_IMMUTABLE');end if;
end;
/
