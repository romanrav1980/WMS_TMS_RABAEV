create or replace trigger RRL_OUTBOX_LEASE_G before update or delete on RRL_EVENT_OUTBOX for each row
begin
 if :old.CLAIM_VERSION>0 or (updating and :new.CLAIM_VERSION>0)then
  if deleting or RRL_OUTBOX_DELIVERY_API.write_allowed(:old.EVENT_OUTBOX_ID)!=1 then
   raise_application_error(-20863,'OUTBOX_FENCED_DELIVERY_ONLY');end if;
 end if;
end;
/
create or replace trigger RRL_ADAPTER_LEASE_G before update or delete on RRL_ADAPTER_REQUEST_LOG for each row
begin
 if :old.CLAIM_VERSION>0 or (updating and :new.CLAIM_VERSION>0)then
  if deleting or RRL_OUTBOX_DELIVERY_API.write_allowed(:old.EVENT_OUTBOX_ID)!=1 then
   raise_application_error(-20863,'OUTBOX_FENCED_RESPONSE_ONLY');end if;
 end if;
end;
/
