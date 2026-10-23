declare s clob;n number;
 procedure same(p_name varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_STOCK_POOL_READ','761B51CA2258159170DD40C50C988CAD6C1B706FE7577A31CD439C4A9DA126C1','AFTER_SOURCE_MISMATCH');
 same('RRL_STOCK_POOL_CMD','76AC3806FD7FF7C41D02B318D6A373694B3D364D36C7508C0162A6DE3621A6B3','AFTER_SOURCE_MISMATCH');
 same('RRL_TRADE_TOPUP_ADOPT','8AA8EBBAA8C2BE720B7ABD6D78106E128F0213E1F2E12D378629BB73D2AD454A','AFTER_SOURCE_MISMATCH');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_STOCK_POOL_READ','RRL_STOCK_POOL_CMD','RRL_TRADE_TOPUP_ADOPT');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;
end;
/
