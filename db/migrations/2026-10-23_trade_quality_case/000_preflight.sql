declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TRADE_QUALITY_CASE','RRL_TRADE_QUALITY_CASE_UNIT','RRL_TRADE_QUALITY_CASE_EVENT','RRL_TRADE_QUALITY_CASE_SQ','RRL_TRADE_QUALITY_CASE_API','RRL_TRADE_QUALITY_CASE_EVENT_APPEND','RRL_TRADE_QUALITY_CASE_UNIT_FROZEN');
 if n<>0 then raise_application_error(-20999,'QUALITY_OBJECTS_ALREADY_PRESENT');end if;
 select count(*)into n from USER_TABLES where TABLE_NAME in('RRL_TRADE_SITE','RRL_ACCESS_REV','RRL_WMS_RECEIPT_UNIT','RRL_TRADE_STOCK_ATTR','RRL_REMAINS','RRL_CELLS','RRL_INVENTORY_TASK','RRL_QUALITY_HOLD');
 if n<>8 then raise_application_error(-20999,'QUALITY_DEPENDENCIES_MISSING');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TRADE_STOCK_GUARD','RRL_ACCESS_API','RRL_STOCK_PLAN_HELPER','RRL_TRACEABILITY_API')and OBJECT_TYPE='PACKAGE BODY'and STATUS='VALID';
 if n<>4 then raise_application_error(-20999,'QUALITY_PACKAGES_MISSING');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;
end;
/
