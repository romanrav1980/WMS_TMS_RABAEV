@@after_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/
declare n number;begin
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME='RRL_IW_CASE_CARRIER'and STATUS!='ENABLED';if n!=0 then raise_application_error(-20886,'CASE_BRIDGE_CONSTRAINT_INVALID');end if;
 select count(*)into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_IW_GROUP_REC_ST_UQ';if n!=0 then raise_application_error(-20886,'CASE_BRIDGE_MULTI_LEAF_ST_STILL_UNIQUE');end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_GREC_SOURCE_ST_IX'and UNIQUENESS='NONUNIQUE'and STATUS='VALID';if n!=1 then raise_application_error(-20886,'CASE_BRIDGE_SOURCE_ST_LOOKUP_INDEX_REQUIRED');end if;
end;
/
