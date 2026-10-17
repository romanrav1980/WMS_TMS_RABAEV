declare a clob;n number;begin
 dbms_lob.createtemporary(a,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_WH_WEIGH_REQUEST_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='6056CF3B8CE3FE3F71BCA1CB0C030F3AD73C834A78C911B6CF6201E7A20CE3E8'then raise_application_error(-20886,'WH_ZERO_EXACT_SOURCE_RRL_WH_WEIGH_REQUEST_API');end if;
 dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_WH_WEIGH_REQUEST_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A384012E3557C3A87047B787D1812C939FE17FA80D1B386EAF49FBE2E2E66D6D'then raise_application_error(-20886,'WH_ZERO_EXACT_SOURCE_RRL_WH_WEIGH_REQUEST_API');end if;
 dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_WH_WEIGH_ZERO_GUARD'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='FBE69CD66768C99FE95C78DE794172C6BC3C69DE9418819AC0097DFE15358B2D'then raise_application_error(-20886,'WH_ZERO_EXACT_SOURCE_RRL_WH_WEIGH_ZERO_GUARD');end if;
 dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_WH_SCALE_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='AACBA7EF3C676C11664CE1CB9A394052B91EE0B7D487BAEED1780C1D969A7269'then raise_application_error(-20886,'WH_ZERO_EXACT_SOURCE_RRL_WH_SCALE_API');end if;
 dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_ASSEMBLY_SCALE_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='3959831FE6663ECA0049CAED70ED6FE0C00570B61732A491CD0BA55A03774159'then raise_application_error(-20886,'WH_ZERO_EXACT_SOURCE_RRL_ASSEMBLY_SCALE_API');end if;
 dbms_lob.freetemporary(a);
end;
/
