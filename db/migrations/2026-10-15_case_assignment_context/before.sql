declare n number;begin
 select count(*)into n from ALL_CONTEXT where NAMESPACE='RRL_CASE_ASSIGNMENT_CTX';if n!=0 then raise_application_error(-20886,'CASE_ASSIGNMENT_CONTEXT_EXPECTED_ABSENT');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_CASE_ASSIGNMENT_API'and OBJECT_TYPE='PACKAGE'and STATUS='VALID';if n!=1 then raise_application_error(-20886,'CASE_ASSIGNMENT_OWNER_REQUIRED');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'GLOBAL_INVALID_BEFORE');end if;
end;
/
