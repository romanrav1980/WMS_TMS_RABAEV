declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_INVENTORY_CMD'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='82C7A42A38D72C28391C94E084E457BACCC2B29B26E89F52E3EF9A842630C30D'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_INVENTORY_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_INVENTORY_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7183BB356163BCF03087A471F7C00EE1C72B21928098A1AE9D310C61AFEF3D6D'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_INVENTORY_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOCK_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A2A901D6EA732405798062603EB483DD294CF9E67DBCFE8BD36501300FB53C30'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_LOCK_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOCK_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='7E18653D8CAD1F59D67BAA92E5DC761E1C4C6708D92B0F5D31BEFAE663B84F81'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_LOCK_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='52AF65674B75A4C5365F1CF91F26D7FFC47F67775AF3D8B15FA7CA3230E673F0'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_POSTING_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_SHORT_RECOVERY'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='E57E7D5A5DA080E3A37DE4B662A3241AF2F88A36B781C753CD2D850CB27B8017'then raise_application_error(-20886,'INV_SCOPE_SOURCE_RRL_STOCK_SHORT_RECOVERY');end if;dbms_lob.freetemporary(a);
end;
/
