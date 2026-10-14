create or replace trigger RRL_TT_LOADED_ST_ASSIGN_GUARD before update of TRANSTASK_ID,ADDR or delete on RRL_SBORKA_PALLETS for each row
declare n number;
begin
 if updating and nvl(:new.TRANSTASK_ID,0)=nvl(:old.TRANSTASK_ID,0) and nvl(:new.ADDR,chr(0))=nvl(:old.ADDR,chr(0)) then return;end if;
 select count(*) into n from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID
  where ls.SBORKA_PALLET_ID=:old.ID and ls.ACTIVE_FLAG=1 and lf.STATUS in('LOADED','DEPARTED');
 if n>0 then raise_application_error(-20886,'LOADED_ST_CONFIRMED_UNLOADING_REQUIRED');end if;
end;
/
