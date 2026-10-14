create or replace trigger RRL_WTASK_FINISH_TIME_GUARD
before insert or update of STATUS,FINISHED_AT_INSTANT on RRL_WAREHOUSE_TASK for each row
begin
 if inserting then
  if :new.FINISHED_AT_INSTANT is not null then raise_application_error(-20863,'TASK_NEW_FINISH_CLOCK_NOT_ALLOWED');end if;
 else
  if :old.FINISHED_AT_INSTANT is not null and(:new.FINISHED_AT_INSTANT is null or :new.FINISHED_AT_INSTANT!=:old.FINISHED_AT_INSTANT)then
   raise_application_error(-20863,'TASK_FINISH_CLOCK_IMMUTABLE');
  end if;
  if nvl(:old.STATUS,'~')!='DONE'and :new.STATUS='DONE'then
   :new.FINISHED_AT_INSTANT:=systimestamp;
  elsif :old.FINISHED_AT_INSTANT is null and :new.FINISHED_AT_INSTANT is not null then
   raise_application_error(-20863,'TASK_HISTORICAL_FINISH_CLOCK_REQUIRES_EXPLICIT_SOURCE');
  end if;
 end if;
end;
/
