-- Pre-apply INVALID baseline must be zero; compile only invalid project dependents after new specs.
begin
 dbms_utility.compile_schema(schema=>user,compile_all=>false);
end;
/
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_ASSEMBLY_SCALE_API','RRL_SCALE_PACKET_READ','RRL_CASE_SCALE_ADMISSION','RRL_STOCK_CASE_PICK_CMD')or NAME like 'RRL_ASM_%GUARD';
 if n!=0 then raise_application_error(-20886,'ASSEMBLY_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'ASSEMBLY_GLOBAL_INVALID');end if;
end;
/
