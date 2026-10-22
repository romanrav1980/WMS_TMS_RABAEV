declare s clob;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,'SOURCE_NOT_APPLIED:'||p_name);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 same('RRL_STOCK_RESERVE_CORE','PACKAGE','E3D9A92AB3687ADDFB532BC6DB39DEAC59114B79C7EA3BEC122C5F72EC1D6FF0');
 same('RRL_STOCK_RESERVE_CORE','PACKAGE BODY','9E863E177718CAF508FFE5E17498EF6A5A044B945713E02C09555043D8B31F4B');
 same('RRL_PICKING_API','PACKAGE BODY','43D221DCB8DC20A4635B644826E30A96EEE83EC1978C217C4C3B66E93BC181AC');
 same('RRL_STOCK_WAVE_LAUNCH_CMD','PACKAGE BODY','6CAFD4647851C0E267C6557391829463829D7FC19219F42560BB85D086B54DB7');
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE BODY','204D42072234011B1903806E97AA5279875C293AD6BB443ECD825A739EC3FC91');
end;
/
declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_TRADE_TOPUP_ADOPT','RRL_STOCK_RESERVE_CORE','RRL_STOCK_RESERVE_CORE','RRL_PICKING_API','RRL_STOCK_WAVE_LAUNCH_CMD','RRL_TRADE_PICK_CONTEXT');
 if n<>0 then raise_application_error(-20999,'TOPUP_COMPILE_ERRORS');end if;
 select count(*)into n from USER_TABLES where TABLE_NAME in('RRL_TRADE_TOPUP_ADOPTION');if n<>1 then raise_application_error(-20999,'TOPUP_TABLES_MISSING');end if;
end;
/
