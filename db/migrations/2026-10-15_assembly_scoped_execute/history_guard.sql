declare n number;begin
 select count(*)into n from RRL_ASSEMBLY_SESSION;if n!=3 then raise_application_error(-20886,'ASM_SCOPE_HISTORY_RRL_ASSEMBLY_SESSION');end if;
 select count(*)into n from RRL_ASSEMBLY_STEP;if n!=3 then raise_application_error(-20886,'ASM_SCOPE_HISTORY_RRL_ASSEMBLY_STEP');end if;
 select count(*)into n from RRL_ASSEMBLY_CAPTURE;if n!=6 then raise_application_error(-20886,'ASM_SCOPE_HISTORY_RRL_ASSEMBLY_CAPTURE');end if;
 select count(*)into n from RRL_ASSEMBLY_STEP_USE;if n!=1 then raise_application_error(-20886,'ASM_SCOPE_HISTORY_RRL_ASSEMBLY_STEP_USE');end if;
 select count(*)into n from RRL_ASM_INTENT_ABANDON;if n!=2 then raise_application_error(-20886,'ASM_SCOPE_HISTORY_RRL_ASM_INTENT_ABANDON');end if;
 select count(*)into n from RRL_WH_SCALE_CAPTURE;if n!=79 then raise_application_error(-20886,'ASM_SCOPE_HISTORY_RRL_WH_SCALE_CAPTURE');end if;
 select count(*)into n from RRL_CASE_PICK_EVENT;if n!=1401 then raise_application_error(-20886,'ASM_SCOPE_HISTORY_RRL_CASE_PICK_EVENT');end if;
end;
/
