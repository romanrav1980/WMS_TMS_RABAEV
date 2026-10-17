declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='0EB209D4360E488263984FF9F01ED8BF928551BD104EBE0FA23C5877D98205CE'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_POSTING_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_UNLOAD_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='61C7F440218F0FC2B4E2BAB0B0AEE3B873AC18C996474398E94725791D07DBD9'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_UNLOAD_CMD');end if;dbms_lob.freetemporary(a);
end;
/
