create or replace trigger RRL_PICKER_TIME_STREAM_G before insert or update or delete on RRL_PICKER_TIME_STREAM for each row
begin
 if deleting or RRL_PICKER_TIME_API.write_allowed(:new.OPERATOR_ID)!=1 then raise_application_error(-20886,'PICKER_TIME_TRUSTED_STREAM_OWNER_REQUIRED');end if;
 if inserting then
  if :new.STREAM_VERSION is null or :new.STREAM_VERSION!=1 then raise_application_error(-20886,'PICKER_TIME_DERIVED_VERSION_REQUIRED');end if;
 elsif :new.OPERATOR_ID!=:old.OPERATOR_ID or :new.STREAM_VERSION is null or :new.STREAM_VERSION!=:old.STREAM_VERSION+1
  or :new.LAST_EVENT_AT is null or :new.LAST_EVENT_AT<:old.LAST_EVENT_AT then raise_application_error(-20886,'PICKER_TIME_DERIVED_VERSION_REQUIRED');end if;
end;
/
create or replace trigger RRL_PICKER_TIME_EVENT_G before insert or update or delete on RRL_PICKER_TIME_EVENT for each row
begin
 if not inserting or RRL_PICKER_TIME_API.write_allowed(:new.OPERATOR_ID)!=1 then raise_application_error(-20886,'PICKER_TIME_EVENT_APPEND_ONLY');end if;
end;
/
create or replace trigger RRL_PICKER_TIME_SPAN_G before insert or update or delete on RRL_PICKER_TIME_SPAN for each row
begin
 if not inserting or RRL_PICKER_TIME_API.write_allowed(:new.OPERATOR_ID)!=1 then raise_application_error(-20886,'PICKER_TIME_SPAN_APPEND_ONLY');end if;
end;
/
create or replace trigger RRL_PICKER_TIME_COMMAND_G before insert or update or delete on RRL_PICKER_TIME_COMMAND for each row
begin
 if not inserting or RRL_PICKER_TIME_API.write_allowed(:new.ACTOR_ID)!=1 then raise_application_error(-20886,'PICKER_TIME_COMMAND_APPEND_ONLY');end if;
end;
/
