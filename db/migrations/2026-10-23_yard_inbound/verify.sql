declare s clob;n number;begin
 if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_YARD_VISIT_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'1BD9DF2572541AE6FB058DA42D4E600B3D3579213894C35F4E05952BA306798A'then raise_application_error(-20999,'YARD_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(s);
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_YARD_VISIT_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'C3FF494DB2DF2F6D5AAB8C87918537BD71D82EB6CDDB874E5D82E54D59E7EC84'then raise_application_error(-20999,'YARD_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(s);
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
