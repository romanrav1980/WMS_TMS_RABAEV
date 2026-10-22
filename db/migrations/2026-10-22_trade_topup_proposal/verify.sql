declare s clob;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,'SOURCE_NOT_APPLIED:'||p_name);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 same('RRL_STOCK_POSTING_API','PACKAGE BODY','17D2E04E9418FEE3594DEC9F45933CDBF93CADA9E27770E9191A957019BC933D');
 same('RRL_TRADE_STOCK_GUARD','PACKAGE BODY','AB52B7FCBE3A59ED7412030B4DC93D7282674FAE1F0A51AE80C9A7AB5963667F');
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE BODY','E88CB4256EFA8DB7EDB12C83CF4707F442E48A34DF241CD9E059431ECC423E6E');
 same('RRL_STOCK_RESERVE_CORE','PACKAGE','5804CF404AE2F236EFD8844471F43BDD8B291C17698968C67A724738910E41A5');
 same('RRL_STOCK_UNIT_CORE','PACKAGE','8C37F4D9C5152401C6060DB172140AB53F0A69F058EC924F1704DD195E590EEC');
end;
/
declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_TRADE_TOPUP_READ','RRL_TRADE_TOPUP_API','RRL_TRADE_TOPUP_CMD','RRL_STOCK_POSTING_API','RRL_TRADE_STOCK_GUARD','RRL_TRADE_PICK_CONTEXT','RRL_STOCK_RESERVE_CORE','RRL_STOCK_UNIT_CORE');
 if n<>0 then raise_application_error(-20999,'TOPUP_COMPILE_ERRORS');end if;
 select count(*)into n from USER_TABLES where TABLE_NAME in('RRL_TRADE_TOPUP_EVENT','RRL_TRADE_TOPUP_HOLD','RRL_TRADE_TOPUP_DECISION','RRL_TRADE_TOPUP_PROPOSAL');if n<>4 then raise_application_error(-20999,'TOPUP_TABLES_MISSING');end if;
end;
/
