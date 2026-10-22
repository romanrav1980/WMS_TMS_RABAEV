declare s clob;n number;begin
 if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_INTERNAL_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'555BDCBFDB82D23AF18F92604655EF6E8AA54A9DB1785BFA4ED2BD8B93681A53'then raise_application_error(-20999,'QUARANTINE_SCOPE_SOURCE_MISMATCH');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
