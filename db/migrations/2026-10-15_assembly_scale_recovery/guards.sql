create or replace trigger RRL_ASM_RECON_GUARD before insert or update or delete on RRL_ASM_RECONCILIATION for each row begin
 if deleting or RRL_ASSEMBLY_RECOVERY_API.write_allowed!=1 then raise_application_error(-20863,'ASSEMBLY_RECONCILIATION_OWNER_REQUIRED');end if;
 if updating and(:new.RECONCILIATION_ID!=:old.RECONCILIATION_ID or :new.SESSION_ID!=:old.SESSION_ID or :new.STEP_ID!=:old.STEP_ID
  or :new.EXPECTED_CONTENT_VERSION!=:old.EXPECTED_CONTENT_VERSION or :new.EXPECTED_WEIGHT_KG!=:old.EXPECTED_WEIGHT_KG
  or :new.REQUESTER_ID!=:old.REQUESTER_ID or dbms_lob.compare(:new.REQUEST_JSON,:old.REQUEST_JSON)!=0
  or dbms_lob.compare(:new.REQUEST_RESULT,:old.REQUEST_RESULT)!=0)then raise_application_error(-20863,'ASSEMBLY_RECONCILIATION_IMMUTABLE_IDENTITY');end if;
end;
/
create or replace trigger RRL_ASM_RECON_CAPTURE_GUARD before insert or update or delete on RRL_ASM_RECON_CAPTURE for each row begin
 if updating or deleting or RRL_ASSEMBLY_RECOVERY_API.write_allowed!=1 then raise_application_error(-20863,'ASSEMBLY_RECONCILIATION_CAPTURE_APPEND_ONLY');end if;
end;
/
