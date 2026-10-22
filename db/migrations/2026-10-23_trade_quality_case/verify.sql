declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME='RRL_TRADE_QUALITY_CASE_API';if n<>0 then raise_application_error(-20999,'QUALITY_COMPILE_ERRORS');end if;
 select count(*)into n from USER_TABLES where TABLE_NAME in('RRL_TRADE_QUALITY_CASE','RRL_TRADE_QUALITY_CASE_UNIT','RRL_TRADE_QUALITY_CASE_EVENT');
 if n<>3 then raise_application_error(-20999,'QUALITY_TABLES_MISSING');end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_TRADE_QUALITY_CASE_ACTIVE_UK'and UNIQUENESS='UNIQUE';
 if n<>1 then raise_application_error(-20999,'QUALITY_ACTIVE_GUARD_MISSING');end if;
 select count(*)into n from USER_TRIGGERS where TRIGGER_NAME in('RRL_TRADE_QUALITY_CASE_EVENT_APPEND','RRL_TRADE_QUALITY_CASE_UNIT_FROZEN')and STATUS='ENABLED';
 if n<>2 then raise_application_error(-20999,'QUALITY_EVIDENCE_GUARDS_MISSING');end if;
end;
/
