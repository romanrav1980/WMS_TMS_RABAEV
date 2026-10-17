declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOCK_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A2A901D6EA732405798062603EB483DD294CF9E67DBCFE8BD36501300FB53C30'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_LOCK_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOCK_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7E18653D8CAD1F59D67BAA92E5DC761E1C4C6708D92B0F5D31BEFAE663B84F81'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_LOCK_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_PLAN_HELPER'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7A1E25DA05977D7AE09A4323C66BB7E2EAD8A6DA395F5DD7D2B1A11B65A95B0D'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_PLAN_HELPER');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STORE_UNLOAD_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='9E2A133C4DFB7B003184816F54DDA70EC949BAF988BEAFEB79C85DC726B75DE0'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STORE_UNLOAD_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STORE_UNLOAD_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='2B30DE381CE6E9D7BB44643628124F3CAAA42FD1CCE7779C88E535F48ED3D0E2'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STORE_UNLOAD_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STORE_UNLOAD_START_G'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7B755725FA5C7CEE47B8B3F458CC150113A9B79304D525F52235B41FE7594FE4'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STORE_UNLOAD_START_G');end if;dbms_lob.freetemporary(a);
end;
/
