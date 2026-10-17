@@after_sources.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'ASM_SCOPE_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'ASM_SCOPE_GLOBAL_INVALID');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_ASM_META_SCOPE'and OBJECT_TYPE in('PACKAGE','PACKAGE BODY')and STATUS='VALID';if n!=2 then raise_application_error(-20886,'ASM_SCOPE_TRUSTED_PACKAGE_PAIR');end if;
end;
/
