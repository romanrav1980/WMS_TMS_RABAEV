@@after_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/
declare n number;begin
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME in('RRL_DELIVERY_WINDOW','RRL_DELIVERY_ARRIVAL')and(STATUS!='ENABLED'or VALIDATED!='VALIDATED');
 if n!=0 then raise_application_error(-20886,'DELIVERY_TIME_CONSTRAINTS');end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME in('RRL_DELIV_WINDOW_WARE_IX','RRL_DELIV_ARRIVAL_WARE_IX')and STATUS='VALID';
 if n!=2 then raise_application_error(-20886,'DELIVERY_TIME_INDEXES');end if;
end;
/
declare result_value clob;begin
 begin
  RRL_DELIVERY_TIME_API.plan_window('{"operation_id":"DELIVERY16.CONTEXT.PROBE","load_operation_id":"DELIVERY16.NEVER.EXISTS.CONTEXT.PROBE","store_address":"NONE","reason":"Native context ownership probe"}','admin',result_value);
  raise_application_error(-20886,'DELIVERY_CONTEXT_PROBE_UNEXPECTED_LOAD');
 exception when no_data_found then null;end;
 rollback;
 begin
  dbms_session.set_context('RRL_DELIVERY_TIME_CTX','OPERATION_ID','OUTSIDE.PROBE');
  raise_application_error(-20886,'DELIVERY_OUTSIDE_CONTEXT_WRITE_ALLOWED');
 exception when others then if SQLCODE!=-1031 then raise;end if;end;
end;
/
