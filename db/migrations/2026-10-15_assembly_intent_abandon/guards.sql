create or replace trigger RRL_ASM_INTENT_GUARD before insert or update or delete on RRL_ASM_INTENT_ABANDON for each row begin
 if updating or deleting or RRL_ASM_INTENT_API.write_allowed!=1 then raise_application_error(-20863,'ASSEMBLY_INTENT_LEDGER_APPEND_ONLY');end if;
end;
/
