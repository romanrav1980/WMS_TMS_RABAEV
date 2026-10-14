create or replace trigger RRL_HU_TARE_LINK_GUARD before insert or update on RRL_WMS_HU_LINK for each row
declare n number;
begin
 if :new.ACTIVE_FLAG!=1 then return;end if;
 if updating and :old.ACTIVE_FLAG=1 and :old.PARENT_UID=:new.PARENT_UID and nvl(:old.CHILD_PALLET_UID,'~')=nvl(:new.CHILD_PALLET_UID,'~') and nvl(:old.CHILD_CASE_TASK_ID,-1)=nvl(:new.CHILD_CASE_TASK_ID,-1)then return;end if;
 select count(*) into n from RRL_TARE_BOOK where STATUS='HELD' and((PLACE_KIND='HU' and PLACE_ID=:new.CHILD_PALLET_UID)or(PLACE_KIND='CASE' and PLACE_ID=to_char(:new.CHILD_CASE_TASK_ID,'TM9')));
 if n!=0 then raise_application_error(-20886,'TARE_BOOKED_CHILD_REPACK_PROOF_REQUIRED');end if;
end;
/
