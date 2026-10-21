declare s clob;n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_STOCK_GUARD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256))<>'590C2A2D4C275278E9081662FC0B98CCBBA4B9165A049B9721D45ED3F6995655'then raise_application_error(-20999,'TRADE_GUARD_SOURCE_DRIFT');end if;
 dbms_lob.freetemporary(s);
end;
/
