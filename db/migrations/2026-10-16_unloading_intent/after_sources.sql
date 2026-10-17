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
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='FBE57AD27D3BCF23082D55A92A37C9064D54674ED7BE8FBFD224DCE734677E3E'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STORE_UNLOAD_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STORE_UNLOAD_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='EC1AFA539FA0A06F8342297630896BC47B1D9F5D252B44ACCABC0D6C22957D99'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STORE_UNLOAD_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STORE_UNLOAD_START_G'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7B755725FA5C7CEE47B8B3F458CC150113A9B79304D525F52235B41FE7594FE4'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STORE_UNLOAD_START_G');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_UNLOAD_INTENT_GUARD'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7D7834CF57774B92F3CFC2A4EC173A84EE774957A6670EF1578251EF1CFA1DC2'then raise_application_error(-20886,'SOURCE_GUARD_RRL_UNLOAD_INTENT_GUARD');end if;dbms_lob.freetemporary(a);
end;
/
