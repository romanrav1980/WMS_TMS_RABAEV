declare n number;begin select count(*)into n from USER_ERRORS where NAME='RRL_ASSEMBLY_SCALE_API';if n!=0 then raise_application_error(-20886,'ASM_SHIPPING_CONTEXT_COMPILE_ERRORS');end if;select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'ASM_SHIPPING_CONTEXT_INVALID_AFTER');end if;end;
/
