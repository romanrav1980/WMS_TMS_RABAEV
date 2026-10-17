declare n number;begin
 select count(*)into n from ALL_CONTEXT where NAMESPACE='RRL_CASE_ASSIGNMENT_CTX'and PACKAGE='RRL_CASE_ASSIGNMENT_API'and SCHEMA=user;if n!=1 then raise_application_error(-20886,'CASE_ASSIGNMENT_CONTEXT_BINDING_REQUIRED');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'GLOBAL_INVALID_AFTER');end if;
end;
/
