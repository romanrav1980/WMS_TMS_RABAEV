declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_TRADE_DOCUMENT_API','PACKAGE BODY','DBFE94BF22705395208A14082480FA04B48808CB45B02D495A836B593F63596A','AFTER_SOURCE_MISMATCH');
 same('RRL_TRADE_ORDER_API','PACKAGE BODY','AC41B2AA980FAB902A578BF9078F89C1B667C64254B599DD1855F0CB74935689','AFTER_SOURCE_MISMATCH');
 same('RRL_TRADE_DOCUMENT_API','PACKAGE','99158EB4546B739E4E9EB3A0FAAEDCF4C6AC3F5F0A4329D15C91BDA846D1BDE0','DEPENDENCY_CHANGED');
 same('RRL_TRADE_ORDER_API','PACKAGE','9168989E0B7BEA4B865B746B3319097C9226CA25C4F2D43950E3BD183A76B170','DEPENDENCY_CHANGED');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_TRADE_DOCUMENT_API','RRL_TRADE_ORDER_API');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;
end;
/
