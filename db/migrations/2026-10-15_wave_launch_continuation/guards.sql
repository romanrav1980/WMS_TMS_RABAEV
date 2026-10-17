create or replace trigger RRL_WAVE_CONTINUE_GUARD before insert or update or delete on RRL_WAVE_CONTINUE
begin
 if RRL_WAVE_CONTINUE_API.writing!=1 then raise_application_error(-20882,'WAVE_CONTINUATION_NATIVE_WRITER_REQUIRED');end if;
end;
/
create or replace trigger RRL_WAVE_CONTINUE_STEP_GUARD before insert or update or delete on RRL_WAVE_CONTINUE_STEP
begin
 if RRL_WAVE_CONTINUE_API.writing!=1 then raise_application_error(-20882,'WAVE_CONTINUATION_NATIVE_WRITER_REQUIRED');end if;
end;
/
create or replace trigger RRL_WAVE_CONTINUE_SOURCE_GUARD before insert or update or delete on RRL_WAVE_CONTINUE_SOURCE
begin
 if not inserting then raise_application_error(-20882,'WAVE_SOURCE_INTENTS_APPEND_ONLY');end if;
 if RRL_WAVE_CONTINUE_API.writing!=1 then raise_application_error(-20882,'WAVE_CONTINUATION_NATIVE_WRITER_REQUIRED');end if;
end;
/
