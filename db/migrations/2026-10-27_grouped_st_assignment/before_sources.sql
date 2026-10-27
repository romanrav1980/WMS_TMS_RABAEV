declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_ST_DEFER_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='5D800DD133549D6437984801EC996B02D762B099E40B7768AE0E5E0AE0E8543C'then raise_application_error(-20886,'SOURCE_GUARD_RRL_ST_DEFER_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_PLAN_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A6B5D1F8F9F04A1298C63920CAFE06BB05DACCBEA07713A423BDC6FC0D760703'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TRANSPORT_PLAN_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TT_ADD_PALL'and TYPE='FUNCTION'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='5C29DF7EE069C03647235470F051409CE1FEBC66596CFDEEE45AEC892F9A092C'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TT_ADD_PALL');end if;dbms_lob.freetemporary(a);
end;
/
