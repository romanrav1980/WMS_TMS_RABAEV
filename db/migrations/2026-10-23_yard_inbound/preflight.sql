declare s clob;n number;begin
 if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_YARD_VISIT_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'4F481E4B97E3C3F7DC892C1F8A8EAF98A96D3A2C4EAB219EA87DC55F9AE4D52D'then raise_application_error(-20999,'YARD_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(s);
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_YARD_VISIT_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'46E4C481E76CCDD5E62B0023AE96BB995C115561B209638F22A942E0D0C5BADA'then raise_application_error(-20999,'YARD_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(s);
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_YARD_VISIT_SUPPLY','RRL_YARD_SUPPLY_API','RRL_YARD_SUPPLY_GUARD');if n<>0 then raise_application_error(-20999,'INBOUND_OBJECT_EXISTS');end if;end;
/
