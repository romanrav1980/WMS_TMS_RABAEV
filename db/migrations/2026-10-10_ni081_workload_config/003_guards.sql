create or replace trigger RRL_WORKLOAD_OPERATION_G before insert or update or delete on RRL_WORKLOAD_OPERATION for each row
begin
 if deleting or RRL_WORKLOAD_CONFIG_API.write_allowed(:new.OPERATION_ID)!=1 then raise_application_error(-20863,'WORKLOAD_NATIVE_CONFIG_ONLY');end if;
 if updating and(:new.OPERATION_ID!=:old.OPERATION_ID or :new.REQUEST_HASH!=:old.REQUEST_HASH or :new.ACTOR!=:old.ACTOR or :new.WARE_ID!=:old.WARE_ID or :new.ACTION_KIND!=:old.ACTION_KIND or :new.CREATED_AT!=:old.CREATED_AT)then raise_application_error(-20863,'WORKLOAD_OPERATION_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_WORKLOAD_NORM_G before insert or update or delete on RRL_WORKLOAD_NORM for each row
begin
 if not inserting or RRL_WORKLOAD_CONFIG_API.write_allowed(:new.OPERATION_ID)!=1 then raise_application_error(-20863,'WORKLOAD_IMMUTABLE_NORM_VERSION');end if;
end;
/
create or replace trigger RRL_WORKLOAD_ATTEND_G before insert or update or delete on RRL_WORKLOAD_ATTENDANCE for each row
begin
 if not inserting or RRL_WORKLOAD_CONFIG_API.write_allowed(:new.PLAN_OPERATION_ID)!=1 then raise_application_error(-20863,'WORKLOAD_IMMUTABLE_PLANNED_ATTENDANCE');end if;
end;
/
create or replace trigger RRL_WORKLOAD_CANCEL_G before insert or update or delete on RRL_WORKLOAD_ATTEND_CANCEL for each row
begin
 if not inserting or RRL_WORKLOAD_CONFIG_API.write_allowed(:new.CANCEL_OPERATION_ID)!=1 then raise_application_error(-20863,'WORKLOAD_IMMUTABLE_CANCEL');end if;
end;
/
