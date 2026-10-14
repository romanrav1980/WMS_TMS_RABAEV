create or replace trigger RRL_PLANNER_APPLY_GUARD before insert or update or delete on RRL_PLANNER_APPLY_RESULT for each row
begin
 if not inserting or RRL_TRANSPORT_PLAN_API.apply_write_allowed(:new.PLAN_ID)!=1 then raise_application_error(-20863,'PLANNER_APPLY_RESULT_IMMUTABLE');end if;
end;
/
