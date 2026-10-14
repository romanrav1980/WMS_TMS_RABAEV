-- MIGRATION_ID:2026-10-10-167-case-carrier-close
create or replace trigger RRL_CASE_CLOSE_JOURNAL_G
 before update or delete on RRL_CASE_PICK_EVENT for each row
declare v_kind varchar2(40);
begin
 select json_value(:old.PAYLOAD_JSON,'$.command_kind' returning varchar2(40) null on error) into v_kind from dual;
 if v_kind='CASE_CARRIER_CLOSE'then
  raise_application_error(-20863,'CASE_CLOSE_HISTORY_IMMUTABLE');
 end if;
end;
/
