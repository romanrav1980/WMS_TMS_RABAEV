@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_HU_CONSOL_API';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_NAMESPACE');end if;end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_HU_CONSOL_READ';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_NAMESPACE');end if;end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_HU_CONSOL_PLAN','RRL_HU_CONSOL_MEMBER','RRL_HU_CONSOL_RECEIPT','RRL_HU_CONSOL_PLAN_GUARD','RRL_HU_CONSOL_MEMBER_GUARD','RRL_HU_CONSOL_RECEIPT_GUARD','RRL_HU_CONSOL_ROOT_U1');if n!=0 then raise_application_error(-20886,'CONSOLIDATION_NAMESPACE_NOT_EMPTY');end if;end;
/
