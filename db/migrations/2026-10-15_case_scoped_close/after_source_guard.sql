declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_LIFECYCLE_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='8ED6EB80267413DF7B4C02495907A4EE396B09F5897097F755B936EB7B669861'then raise_application_error(-20886,'CASE_CLOSE_SOURCE_RRL_CASE_LIFECYCLE_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_LIFECYCLE_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='F2233800F1776B824DBA1A4DC03C686D4FCE52E69A68EEE4D7CF2AB4AB017188'then raise_application_error(-20886,'CASE_CLOSE_SOURCE_RRL_CASE_LIFECYCLE_API');end if;dbms_lob.freetemporary(a);
end;
/
