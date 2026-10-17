declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_ACCESS_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='5F23AB1317A104445205EFFA27E3960CA0ADDDF96BF1A1A9D055DC4109B7AEE8'then raise_application_error(-20886,'SOURCE_GUARD_RRL_ACCESS_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_ACCESS_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='4142C392E38DEDA38585C65073DBA7D83C6125FAACD2F378B656F7AA810F9604'then raise_application_error(-20886,'SOURCE_GUARD_RRL_ACCESS_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_HU_CONSOL_LIST'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='DDE5FDA5453C733EC87986658A5FDE57468EA2982A9F8A127033326880F1282F'then raise_application_error(-20886,'SOURCE_GUARD_RRL_HU_CONSOL_LIST');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_HU_CONSOL_LIST'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='202D802220950AFC22D317266DA8D2A156A02C5D084D79DBE191D2391F100BB3'then raise_application_error(-20886,'SOURCE_GUARD_RRL_HU_CONSOL_LIST');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_HU_CONSOL_READ'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='51FA9B38F5AB0FCF870E9B08A11CABA31E79C2665377379EC12C8B4BD8E0B6A3'then raise_application_error(-20886,'SOURCE_GUARD_RRL_HU_CONSOL_READ');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_HU_CONSOL_READ'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='AF080630446D8BE02F94F8B04C7479936686189C4C32B68205E5B12DD467C883'then raise_application_error(-20886,'SOURCE_GUARD_RRL_HU_CONSOL_READ');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_PLAN_HELPER'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7A1E25DA05977D7AE09A4323C66BB7E2EAD8A6DA395F5DD7D2B1A11B65A95B0D'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_PLAN_HELPER');end if;dbms_lob.freetemporary(a);
end;
/
