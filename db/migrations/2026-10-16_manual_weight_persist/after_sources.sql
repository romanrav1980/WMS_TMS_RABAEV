declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_RECEIPT_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='3146F3D93ECEF559350C97BC4DD79C301091005920544320FB16FD1A572B384D'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_RECEIPT_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_WEIGHT_CORE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='394A9F0B7D3107194D6E5D2EE0BAFDE01F4A951BD0C95FBB5167F7AA4860B24A'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_WEIGHT_CORE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STORE_RECEIPT_WEIGHT_GUARD'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='B14036827BEBDF35124FDAD34D37E75FFEC0D44013C646963C3BC9E3BF1A38FA'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STORE_RECEIPT_WEIGHT_GUARD');end if;dbms_lob.freetemporary(a);
end;
/
