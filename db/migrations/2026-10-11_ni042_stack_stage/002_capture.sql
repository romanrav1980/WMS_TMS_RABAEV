create or replace trigger RRL_CASE_STACK_STAGE_CAPTURE before insert or update of STACK_STAGE,STACK_POLICY_VERSION on RRL_CASE_PICK_LINE for each row
begin
 if inserting then
  select nvl(max(STACK_STAGE),'MAIN'),nvl(max(POLICY_VERSION),0)into :new.STACK_STAGE,:new.STACK_POLICY_VERSION from RRL_SKU_RECEIPT_POLICY where ARTICUL=:new.ARTICUL;
 elsif :new.STACK_STAGE!=:old.STACK_STAGE or :new.STACK_POLICY_VERSION!=:old.STACK_POLICY_VERSION or :new.STACK_STAGE is null or :new.STACK_POLICY_VERSION is null then
  raise_application_error(-20863,'CASE_ISSUED_STACK_STAGE_IMMUTABLE');
 end if;
end;
/
