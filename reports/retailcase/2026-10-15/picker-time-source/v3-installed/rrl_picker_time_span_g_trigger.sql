create or replace trigger RRL_PICKER_TIME_SPAN_G before insert or update or delete on RRL_PICKER_TIME_SPAN for each row
begin
 if not inserting or RRL_PICKER_TIME_API.write_allowed(:new.OPERATOR_ID)!=1 then raise_application_error(-20886,'PICKER_TIME_SPAN_APPEND_ONLY');end if;
end;
/
