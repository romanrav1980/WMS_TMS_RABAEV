declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_ACCESS_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='5F23AB1317A104445205EFFA27E3960CA0ADDDF96BF1A1A9D055DC4109B7AEE8'then raise_application_error(-20886,'SOURCE_GUARD_RRL_ACCESS_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_ACCESS_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='4142C392E38DEDA38585C65073DBA7D83C6125FAACD2F378B656F7AA810F9604'then raise_application_error(-20886,'SOURCE_GUARD_RRL_ACCESS_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_READ'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='8344C651B5CDA4CBE5B8A7D49ECC2B267F211F80BF170ABD3CBE17D95B934F48'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_HU_READ');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_READ'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='803C68EB33CC63B6A6B78E51639E6E0F528F2923F8BFD7D2E8E8E0B4BA67EC0D'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_HU_READ');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_SHIP_CMD'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='9BFDD25B23EE98476DB952EB4FA4E2992EC19D6F46C4C1FCFB7C3369D714AA9B'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_HU_SHIP_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_SHIP_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='950765C06B4EC33A666F0C0ABC92DC43FADD79E5FDFFD995D91055BC3678F95C'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_HU_SHIP_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOCK_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A2A901D6EA732405798062603EB483DD294CF9E67DBCFE8BD36501300FB53C30'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_LOCK_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_PLAN_HELPER'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7A1E25DA05977D7AE09A4323C66BB7E2EAD8A6DA395F5DD7D2B1A11B65A95B0D'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_PLAN_HELPER');end if;dbms_lob.freetemporary(a);
end;
/
