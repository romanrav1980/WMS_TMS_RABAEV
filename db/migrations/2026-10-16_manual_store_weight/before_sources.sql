declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_RECEIPT_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='3146F3D93ECEF559350C97BC4DD79C301091005920544320FB16FD1A572B384D'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_RECEIPT_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_RECEIPT_READ'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='59B5DF7502FC4572809A4E93DE95F85900C33F812DC8835EC8CD06B95726425B'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_RECEIPT_READ');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_RECEIPT_READ'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='75C643D5C7844834073C3420D590CB8A0C35D1A26D6D37BD6E0EA45196DE57E2'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_RECEIPT_READ');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_WEIGHT_CORE'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='CAA68E826C229DA4D9C18C91773174B0351459E816E1A12710A53F77DC22D2A3'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_WEIGHT_CORE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_WEIGHT_CORE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D26A5F3256A6F5160CC2E3225DB4BBB46B1D308D16CFAC7130B3EBEE4652E0C1'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_WEIGHT_CORE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STORE_RECEIPT_WEIGHT_GUARD'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='B14036827BEBDF35124FDAD34D37E75FFEC0D44013C646963C3BC9E3BF1A38FA'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STORE_RECEIPT_WEIGHT_GUARD');end if;dbms_lob.freetemporary(a);
end;
/
