create or replace trigger RRL_VEH_PROFILE_HEAD_GUARD before insert or update or delete on RRL_VEHICLE_PROFILE_HEAD for each row
begin
 if deleting then raise_application_error(-20863,'VEHICLE_PROFILE_HEAD_DELETE_FORBIDDEN');end if;
 RRL_VEHICLE_PROFILE_API.assert_writing;
 if inserting and :new.VERSION_NO!=0 or updating and(:new.VEHICLE_ID!=:old.VEHICLE_ID or :new.VERSION_NO!=:old.VERSION_NO+1)
  then raise_application_error(-20863,'VEHICLE_PROFILE_HEAD_VERSION_REQUIRED');end if;
end;
/
create or replace trigger RRL_VEH_PROFILE_HIST_GUARD before insert or update or delete on RRL_VEHICLE_PROFILE_HIST for each row
begin
 if updating or deleting then raise_application_error(-20863,'VEHICLE_PROFILE_HISTORY_IMMUTABLE');end if;
 RRL_VEHICLE_PROFILE_API.assert_writing;
end;
/
create or replace trigger RRL_TT_VEH_SOURCE_GUARD before insert or update or delete on RRL_TT_VEHICLE_SOURCE for each row
begin
 if updating or deleting then raise_application_error(-20863,'VEHICLE_SOURCE_HISTORY_IMMUTABLE');end if;
 RRL_VEH_DEPART_SOURCE.assert_writing;
 if :new.DEPARTURE_OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')
  then raise_application_error(-20863,'VEHICLE_SOURCE_OPERATION_REQUIRED');end if;
end;
/
