declare s clob;n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_STOCK_GUARD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'4AF17D736EEF8DF4F3112196BDFB0DB689AF5FF6E0A1B5562D08CAA319910E4C'then raise_application_error(-20999,'TRADE_GUARD_SOURCE_DRIFT');end if;
 dbms_lob.freetemporary(s);
end;
/
