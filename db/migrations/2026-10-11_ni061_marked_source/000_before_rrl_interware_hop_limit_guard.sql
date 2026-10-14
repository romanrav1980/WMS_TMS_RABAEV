create or replace trigger RRL_INTERWARE_HOP_LIMIT_GUARD before insert on RRL_INTERWARE_PLAN for each row
declare n number;
begin
 select count(*)into n from RRL_INTERWARE_ONWARD_DISPATCH where OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID;
 if n!=0 then raise_application_error(-20886,'INTERWARE_MULTI_HOP_EXPLICIT_LINEAGE_REQUIRED');end if;
end;
/
