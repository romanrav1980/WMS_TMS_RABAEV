create or replace trigger RRL_CASE_START_TIME_GUARD before insert or update of STARTED_AT_INSTANT,STARTED_SHIFT_TIME_ZONE on RRL_CASE_PICK_TASK for each row
declare n number;zone_text varchar2(64);
begin
 if inserting then
  if :new.STARTED_AT_INSTANT is not null or :new.STARTED_SHIFT_TIME_ZONE is not null then raise_application_error(-20863,'CASE_START_TIME_EXPLICIT_START_REQUIRED');end if;return;
 end if;
 if :old.STARTED_AT_INSTANT is not null then
  if :new.STARTED_AT_INSTANT is null or :new.STARTED_AT_INSTANT!=:old.STARTED_AT_INSTANT or nvl(:new.STARTED_SHIFT_TIME_ZONE,'~')!=nvl(:old.STARTED_SHIFT_TIME_ZONE,'~')then raise_application_error(-20863,'CASE_ACTUAL_START_TIME_IMMUTABLE');end if;return;
 end if;
 if :new.STARTED_AT_INSTANT is null then
  if :new.STARTED_SHIFT_TIME_ZONE is not null then raise_application_error(-20886,'CASE_START_ZONE_WITHOUT_INSTANT');end if;return;
 end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if :old.STARTED_AT is not null then raise_application_error(-20886,'LEGACY_CASE_START_REQUIRES_ORIGINAL_TIME_EVIDENCE');end if;
 if :new.STARTED_AT is null or :new.STARTED_AT_INSTANT<systimestamp-interval '5'second or :new.STARTED_AT_INSTANT>systimestamp+interval '5'second then raise_application_error(-20886,'CASE_START_CURRENT_SERVER_INSTANT_REQUIRED');end if;
 select count(*)into n from RUSERS u join RRL_PICK_WAVE w on w.PICK_WAVE_ID=:new.PICK_WAVE_ID
 where u.ID=:new.UPDATED_BY and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'case_pick_execute')=1 and(u.WARE_ID=w.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 and RRL_CASE_ASSIGNMENT_API.write_allowed(:old.CASE_PICK_TASK_ID,:new.UPDATED_BY,'START')!=1 then raise_application_error(-20882,'CASE_START_CURRENT_BOUND_ACTOR_REQUIRED');end if;
 if nvl(zone_text,'~')!=nvl(:new.STARTED_SHIFT_TIME_ZONE,'~')then raise_application_error(-20886,'CASE_START_ORIGINAL_SHIFT_ZONE_REQUIRED');end if;
end;
/
