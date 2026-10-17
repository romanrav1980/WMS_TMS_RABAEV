declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOAD_BOX_CORE'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='9210D60E5E762251A327B586A8CB368FAC9D543E3ADA21D28F5F0945527B3967'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_LOAD_BOX_CORE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOAD_BOX_CORE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='9E9408EB6CEA929A52CAAE0898562365AA3AA8D13339172EB0EDD2A1EF1F83CA'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_LOAD_BOX_CORE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_CUSTODY_CMD'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D36BDC2524733B1D43096960032094CEB44D1D45F8912D735B7C4985FB79AE7C'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_CUSTODY_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_CUSTODY_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A10C222830D866B1D6E3AD86F8A8F565C74324263F39900FEA4868D23A667157'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_CUSTODY_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_RECEIPT_CMD'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='79CF5A3A835694E67C2B2ADC00ACB351BEC5BDD33251F09F646DE5D8DDF713BC'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_RECEIPT_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_RECEIPT_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='3146F3D93ECEF559350C97BC4DD79C301091005920544320FB16FD1A572B384D'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_RECEIPT_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_RECEIPT_READ'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='59B5DF7502FC4572809A4E93DE95F85900C33F812DC8835EC8CD06B95726425B'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_RECEIPT_READ');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_RECEIPT_READ'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='75C643D5C7844834073C3420D590CB8A0C35D1A26D6D37BD6E0EA45196DE57E2'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_STORE_RECEIPT_READ');end if;dbms_lob.freetemporary(a);
end;
/
