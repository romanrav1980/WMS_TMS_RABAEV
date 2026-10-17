declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WH_WEIGH_REQUEST_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='6056CF3B8CE3FE3F71BCA1CB0C030F3AD73C834A78C911B6CF6201E7A20CE3E8'then raise_application_error(-20886,'WH_EMPTY_SOURCE:RRL_WH_WEIGH_REQUEST_API:PACKAGE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WH_WEIGH_REQUEST_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A384012E3557C3A87047B787D1812C939FE17FA80D1B386EAF49FBE2E2E66D6D'then raise_application_error(-20886,'WH_EMPTY_SOURCE:RRL_WH_WEIGH_REQUEST_API:PACKAGE BODY');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_RESOURCE_POLICY'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D7367AA1BAC23B38B6B8403A5270FA93BC36BC5F44B4398777B6212ECFD7BE25'then raise_application_error(-20886,'WH_EMPTY_SOURCE:RRL_CASE_RESOURCE_POLICY:PACKAGE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_RESOURCE_POLICY'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='E7BC54A226D09F825D2CC6BFAEF75E0591FD8A37A80B0E3E897B8A877B837DCC'then raise_application_error(-20886,'WH_EMPTY_SOURCE:RRL_CASE_RESOURCE_POLICY:PACKAGE BODY');end if;dbms_lob.freetemporary(a);
end;
/
