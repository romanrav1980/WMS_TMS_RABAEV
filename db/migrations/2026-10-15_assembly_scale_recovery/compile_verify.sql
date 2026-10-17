begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_ASSEMBLY_RECOVERY_API','RRL_ASSEMBLY_SCALE_API','RRL_ASM_RECON_GUARD','RRL_ASM_RECON_CAPTURE_GUARD');
 if n!=0 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_GLOBAL_INVALID');end if;
end;
/
