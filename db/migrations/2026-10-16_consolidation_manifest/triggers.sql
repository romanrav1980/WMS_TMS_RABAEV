create or replace trigger RRL_HU_CONSOL_PLAN_GUARD before insert or update or delete on RRL_HU_CONSOL_PLAN for each row
begin
 if deleting then raise_application_error(-20886,'CONSOLIDATION_PLAN_HISTORY_RETAINED');end if;
 RRL_HU_CONSOL_API.assert_write(:new.PLAN_ID);
 if updating and :old.PLAN_ID!=:new.PLAN_ID then raise_application_error(-20886,'CONSOLIDATION_PLAN_ID_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_HU_CONSOL_MEMBER_GUARD before insert or update or delete on RRL_HU_CONSOL_MEMBER for each row
begin
 if deleting then RRL_HU_CONSOL_API.assert_write(:old.PLAN_ID);else RRL_HU_CONSOL_API.assert_write(:new.PLAN_ID);end if;
 if updating and :old.PLAN_ID!=:new.PLAN_ID then raise_application_error(-20886,'CONSOLIDATION_MEMBER_PLAN_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_HU_CONSOL_RECEIPT_GUARD before insert or update or delete on RRL_HU_CONSOL_RECEIPT for each row
begin
 if not inserting then raise_application_error(-20886,'CONSOLIDATION_RECEIPT_IMMUTABLE');end if;
 RRL_HU_CONSOL_API.assert_write(:new.PLAN_ID,:new.OPERATION_ID);
end;
/
