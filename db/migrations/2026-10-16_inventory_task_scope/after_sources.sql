declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_INVENTORY_TASK_ACCESS'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='2275684AC231DDEC115AFFA5ECB641B3778853876F623A55D22E779F475DA261'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_INVENTORY_TASK_ACCESS');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_INVENTORY_TASK_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='DE7E033A992C3B02F1EFBAF31142B93C97838706E954AF435DB95388684D3E19'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_INVENTORY_TASK_ACCESS');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_INVENTORY_CMD'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='82C7A42A38D72C28391C94E084E457BACCC2B29B26E89F52E3EF9A842630C30D'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_INVENTORY_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_INVENTORY_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='84982C5FB169AF20A35537AD1FCA41665139F35E449CD0BEA7545F534AD8A94A'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_INVENTORY_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOCK_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A2A901D6EA732405798062603EB483DD294CF9E67DBCFE8BD36501300FB53C30'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_LOCK_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOCK_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7E18653D8CAD1F59D67BAA92E5DC761E1C4C6708D92B0F5D31BEFAE663B84F81'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_LOCK_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='AE731B15DF41BB6895279D8AB7DAD5324EC771218B089C70CDBC1A8B2F085754'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_POSTING_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_SHORT_RECOVERY'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='910587DC4B95C88D07B9DA8E846E3EE65EACB7FD0D60676F98D31CF55CC0F4CF'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_SHORT_RECOVERY');end if;dbms_lob.freetemporary(a);
end;
/
