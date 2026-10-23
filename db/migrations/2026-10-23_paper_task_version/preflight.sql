declare s clob;n number;begin
 if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_TASK'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'8F91705B227316EDCA9D2CDF14B847F7DB1D6DBABF3BF0A4469E89B05E9055F9'then raise_application_error(-20999,'PAPER_TASK_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(s);
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_MOVE_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'ADB27D680CB686A05E6FBE1F4EF37A3A4C287AD939474C9007CAD5B395E12333'then raise_application_error(-20999,'PAPER_TASK_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(s);
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
