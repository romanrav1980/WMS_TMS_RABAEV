declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOADING_READ'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='24ECE62E208A9B0E457BEC294CC68BEF32F123D35500C8909221ED6F73CA2A2C'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_LOADING_READ');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='4A6D5EEAA59ECED249C7CDBD6C62E9D2A15203928E958A227396A3DF4597A778'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_POSTING_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_SHIPPING_CORE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='FCC89FEF4E4E33BA919E26EED8420463CB7580A7933D91D252BF97E0E28316F8'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_SHIPPING_CORE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_SINGLE_LOAD_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='175FCE42FC25FB923F904587B191799A80EAFE2FD8CF431C855A7494B153CF65'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_SINGLE_LOAD_CMD');end if;dbms_lob.freetemporary(a);
end;
/
