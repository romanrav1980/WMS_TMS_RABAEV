create or replace trigger RRL_TT_MEMBERSHIP_WRITER_GUARD before insert or update of TRANSTASK_ID on RRL_SBORKA_PALLETS for each row
declare tx varchar2(100):=dbms_transaction.local_transaction_id(false);
begin
 if inserting and nvl(:new.TRANSTASK_ID,0)=0 then return;end if;
 if updating and nvl(:new.TRANSTASK_ID,0)=nvl(:old.TRANSTASK_ID,0) then return;end if;
 -- Explicit dev/configuration maintenance owns the existing global CONFIG X fence.
 -- Posting holds the opposing shared fence; ordinary application writes cannot use this mode.
 if sys_context('RRL_STOCK_WRITE_CTX','MODE')='CONFIG' and tx is not null
   and sys_context('RRL_STOCK_WRITE_CTX','TX_ID')=tx then
   RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
   return;
 end if;
 if inserting or tx is null or sys_context('RRL_TT_MEMBERSHIP_CTX','TX_ID') is null
   or sys_context('RRL_TT_MEMBERSHIP_CTX','TX_ID')!=tx
   or sys_context('RRL_TT_MEMBERSHIP_CTX','ST_ID') is null
   or sys_context('RRL_TT_MEMBERSHIP_CTX','ST_ID')!=to_char(:new.ID,'TM9')
   or sys_context('RRL_TT_MEMBERSHIP_CTX','TRIP_ID')!=to_char(nvl(:new.TRANSTASK_ID,0),'TM9') then
   raise_application_error(-20886,'EXPLICIT_TRIP_MEMBERSHIP_WRITER_REQUIRED');
 end if;
end;
/
