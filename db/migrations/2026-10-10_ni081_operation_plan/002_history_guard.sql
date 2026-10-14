create or replace trigger RRL_TT_OP_EXECUTION_GUARD before update or delete on RRL_TT_OPERATIONS for each row
begin
 if deleting then
  if :old.FACT_START is not null or :old.FACT_END is not null then raise_application_error(-20886,'OP_EXECUTION_HISTORY_DELETE_FORBIDDEN');end if;
 elsif updating then
  if (:old.FACT_START is not null and :new.FACT_START is null)or(:old.FACT_END is not null and :new.FACT_END is null)then raise_application_error(-20886,'OP_EXECUTION_HISTORY_CLEAR_FORBIDDEN');end if;
  if (:old.FACT_START is not null or :old.FACT_END is not null)and(
   nvl(:new.ID,-1)!=nvl(:old.ID,-1)or nvl(:new.TT_ID,-1)!=nvl(:old.TT_ID,-1) or nvl(:new.OPERATION_CODE,'~')!=nvl(:old.OPERATION_CODE,'~')or nvl(:new.ORD,-1)!=nvl(:old.ORD,-1)
   or nvl(:new.DURATION_MIN,-1)!=nvl(:old.DURATION_MIN,-1)or nvl(:new.PLAN_START,date'1900-01-01')!=nvl(:old.PLAN_START,date'1900-01-01')
   or nvl(:new.PLAN_END,date'1900-01-01')!=nvl(:old.PLAN_END,date'1900-01-01'))then raise_application_error(-20886,'OP_EXECUTION_PLAN_FROZEN');end if;
 end if;
end;
/
