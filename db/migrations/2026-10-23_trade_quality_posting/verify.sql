declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_STOCK_QUALITY_WRITEOFF','RRL_STOCK_EFFECT_CORE','RRL_STOCK_POSTING_API','RRL_TRADE_STOCK_GUARD',
  'RRL_REGULATORY_STOCK_OUTBOX','RRL_TRADE_QUALITY_CASE_API');
 if n<>0 then raise_application_error(-20999,'QUALITY_POSTING_COMPILE_ERRORS');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_TRADE_QUALITY_CASE'and COLUMN_NAME in('POSTED_BY','POSTED_AT','POST_OPERATION_ID');
 if n<>3 then raise_application_error(-20999,'QUALITY_POSTING_COLUMNS_MISSING');end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME in('RRL_TRADE_QUALITY_CASE_ACTIVE_UK','RRL_TRADE_QUALITY_CASE_POST_UK')and UNIQUENESS='UNIQUE';
 if n<>2 then raise_application_error(-20999,'QUALITY_POSTING_GUARDS_MISSING');end if;
 -- The registrations are present in the shared owners.
 select count(*)into n from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'and TEXT like '%RRL_STOCK_QUALITY_WRITEOFF.%';
 if n<>4 then raise_application_error(-20999,'QUALITY_POSTING_DISPATCH_MISSING');end if;
 select count(*)into n from USER_SOURCE where NAME='RRL_TRADE_STOCK_GUARD'and TYPE='PACKAGE BODY'and TEXT like '%QUALITY_HOLD_ACTIVE%';
 if n<2 then raise_application_error(-20999,'QUALITY_HOLD_GUARD_MISSING');end if;
end;
/
