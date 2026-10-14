create or replace trigger RRL_CLUSTER_CREATE_GUARD before insert or update or delete on RRL_CLUSTER_CREATE_RESULT for each row
begin
 if deleting or RRL_CLUSTER_CREATE_API.write_allowed(:new.OPERATION_ID)!=1 then raise_application_error(-20863,'CLUSTER_RESULT_IMMUTABLE');end if;
 if updating and (:old.RESULT_JSON is not null or :old.OPERATION_ID!=:new.OPERATION_ID or :old.ACTOR!=:new.ACTOR or :old.REQUEST_HASH!=:new.REQUEST_HASH)then
  raise_application_error(-20863,'CLUSTER_RESULT_IMMUTABLE');
 end if;
end;
/
