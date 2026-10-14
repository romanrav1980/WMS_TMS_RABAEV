create or replace trigger RRL_CASE_PALLET_TYPE_GUARD before update of PALLET_TYPE_ID on RRL_CASE_PICK_TASK for each row
begin
 if nvl(:old.PALLET_TYPE_ID,-1)!=nvl(:new.PALLET_TYPE_ID,-1)then RRL_STOCK_CASE_TYPE_CMD.assert_writing(:old.CASE_PICK_TASK_ID);end if;
end;
/
