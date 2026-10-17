@@after_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/
declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_HU_CONSOL_PLAN';if n!=11 then raise_application_error(-20886,'CONSOL_PLAN_COLUMNS');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_HU_CONSOL_MEMBER';if n!=6 then raise_application_error(-20886,'CONSOL_MEMBER_COLUMNS');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_HU_CONSOL_RECEIPT';if n!=8 then raise_application_error(-20886,'CONSOL_RECEIPT_COLUMNS');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME in('RRL_HU_CONSOL_PLAN','RRL_HU_CONSOL_MEMBER','RRL_HU_CONSOL_RECEIPT')and CONSTRAINT_TYPE in('P','U','R','C')and GENERATED='USER NAME'and STATUS='ENABLED'and VALIDATED='VALIDATED';
 if n!=8 then raise_application_error(-20886,'CONSOL_CONSTRAINTS');end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_HU_CONSOL_ROOT_U1'and STATUS='VALID'and UNIQUENESS='UNIQUE';if n!=1 then raise_application_error(-20886,'CONSOL_ACTIVE_ROOT_UNIQUE');end if;
end;
/
