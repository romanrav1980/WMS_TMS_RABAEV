create or replace package RRL_STOCK_SETTING_API authid definer as
 procedure set_compatibility(p_value varchar2,p_reason varchar2,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_SETTING_API as
 procedure set_compatibility(p_value varchar2,p_reason varchar2,p_actor varchar2) is
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();oldvalue varchar2(100);ver number;state varchar2(20);
 begin
  if dbms_transaction.local_transaction_id(false) is not null then raise_application_error(-20862,'SETTING_REQUIRES_CLEAN_TRANSACTION');end if;
  if p_value is null or p_value not in('0','1') or trim(p_reason) is null or length(p_reason)>1000 or p_actor is null
   or RRL_HAS_WRIGHT(p_actor,'stock_compatibility_admin')!=1 then raise_application_error(-20882,'COMPATIBILITY_SETTING_FORBIDDEN');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK',6);RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_LOCK_API.begin_plan;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1 for update;
  if state not in('PREPARED','ACTIVE') then raise_application_error(-20860,'SETTING_RELEASE_CLOSED');end if;
  RRL_STOCK_CTX_API.open_configuration(p_actor,'stock_compatibility_admin');
  select SETTING_VALUE into oldvalue from RRL_SYSTEM_SETTINGS where SETTING_KEY='STOCK_LEGACY_TRIGGER_ENABLED' for update;
  select nvl(max(SETTING_VERSION),0)+1 into ver from RRL_STOCK_SETTING_AUDIT where SETTING_KEY='STOCK_LEGACY_TRIGGER_ENABLED';
  update RRL_SYSTEM_SETTINGS set SETTING_VALUE=p_value,UPDATED_AT=sysdate,UPDATED_BY=p_actor where SETTING_KEY='STOCK_LEGACY_TRIGGER_ENABLED';
  insert into RRL_STOCK_SETTING_AUDIT(SETTING_KEY,SETTING_VERSION,OLD_VALUE,NEW_VALUE,REASON,CHANGED_BY)
   values('STOCK_LEGACY_TRIGGER_ENABLED',ver,oldvalue,p_value,p_reason,p_actor);
  commit;RRL_STOCK_CTX_API.clear_operation;RRL_STOCK_LOCK_API.clear_plan;
 exception when others then rollback;RRL_STOCK_CTX_API.clear_operation;RRL_STOCK_LOCK_API.clear_plan;raise;
 end;
end;
/
