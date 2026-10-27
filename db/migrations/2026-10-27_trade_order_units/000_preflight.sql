declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 same('RRL_TRADE_DOCUMENT_API','PACKAGE BODY','3EBF80AB35E981E45D854F2E0459A6DA9C51EBA3A6948F029F5F5B9BF232A924','BEFORE_SOURCE_DRIFT');
 same('RRL_TRADE_ORDER_API','PACKAGE BODY','2A2924D25138D5A6A21FA3D4CBED034B3DA0EF51416C9B54364ABC5587832381','BEFORE_SOURCE_DRIFT');
 same('RRL_TRADE_DOCUMENT_API','PACKAGE','99158EB4546B739E4E9EB3A0FAAEDCF4C6AC3F5F0A4329D15C91BDA846D1BDE0','DEPENDENCY_DRIFT');
 same('RRL_TRADE_ORDER_API','PACKAGE','9168989E0B7BEA4B865B746B3319097C9226CA25C4F2D43950E3BD183A76B170','DEPENDENCY_DRIFT');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;
end;
/
