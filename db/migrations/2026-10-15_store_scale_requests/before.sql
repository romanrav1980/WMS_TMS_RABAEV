-- MIGRATION_ID: 2026-10-15-store-scale-requests
-- Additive objects only; no pre-existing object is replaced. Stop if names already exist.
declare n number;
begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STORE_WEIGH_REQUEST','RRL_STORE_WEIGH_DEVICE_IDX','RRL_STORE_WEIGH_API','RRL_STORE_WEIGH_GUARD');
 if n!=0 then raise_application_error(-20886,'STORE_WEIGH_ADDITIVE_NAMES_ALREADY_EXIST');end if;
 select count(*) into n from ALL_CONTEXT where NAMESPACE='RRL_STORE_WEIGH_CTX';
 if n!=0 then raise_application_error(-20886,'STORE_WEIGH_CONTEXT_ALREADY_EXISTS');end if;
end;
/
