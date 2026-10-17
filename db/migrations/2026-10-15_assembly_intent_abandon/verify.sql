declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_ASM_INTENT_API','RRL_ASM_INTENT_GUARD','RRL_ASSEMBLY_SCALE_API');if n!=0 then raise_application_error(-20886,'ASM_INTENT_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'ASM_INTENT_INVALID_AFTER');end if;
end;
/
