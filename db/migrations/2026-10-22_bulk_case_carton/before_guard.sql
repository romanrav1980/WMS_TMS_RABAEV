declare s clob;n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_STOCK_GUARD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'B52C46AB5015B7D876D2E04538C802B8580B84FBCBCA0D8B2F739D85FF9B62B4'then raise_application_error(-20999,'TRADE_GUARD_SOURCE_DRIFT');end if;
 dbms_lob.freetemporary(s);
end;
/
