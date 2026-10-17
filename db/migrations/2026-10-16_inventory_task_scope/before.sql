@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'INV_SCOPE_TARGET');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'INV_SCOPE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'INV_SCOPE_INVALID');end if;
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_INVENTORY_TASK_ACCESS';if n!=0 then raise_application_error(-20886,'INV_SCOPE_NAMESPACE');end if;end;
/
