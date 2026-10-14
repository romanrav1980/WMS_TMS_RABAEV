declare n number;
begin
 select count(*) into n from RRL_PICK_WAVE where WAVE_NAME=utl_raw.cast_to_varchar2(hextoraw('4E49434F52415F4D494E494D4158'));
 if n!=0 then raise_application_error(-20801,'PREVIOUS_WAVE_DISPLAY_NAME_REMAINS'); end if;
end;
/
