declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D85B5FCABC365BEAFE91A06F03B6ACBF9E8BB681B42551C5C72E40047B89474A'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_POSTING_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_RETURN_CUST_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='E29EC5DE45A4056840236D0B52458CE1A122FDB01673AD81888E5725F5D3DEAA'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_RETURN_CUST_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_DRIVER_USER_GUARD'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='5BD760BC77332F96CF141E398416700897D587F7DF77FC76AED12A582698A109'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TRANSPORT_DRIVER_USER_GUARD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TT_OPERATION_PLAN_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='1E5B838C99AAE0A4E05A6AF6EA62D0D69713867C0A8C36EBD049A76C63621673'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TT_OPERATION_PLAN_API');end if;dbms_lob.freetemporary(a);
end;
/
