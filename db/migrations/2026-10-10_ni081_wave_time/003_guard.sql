create or replace trigger RRL_WAVE_TIME_PLAN_GUARD before insert or update or delete on RRL_WAVE_TIME_PLAN for each row
begin
 if not inserting or RRL_WAVE_TIME_API.write_allowed(:new.OPERATION_ID)!=1 then raise_application_error(-20863,'WAVE_TIME_PLAN_IMMUTABLE');end if;
end;
/
