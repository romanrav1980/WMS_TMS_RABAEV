declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_INVENTORY_TASK_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='0B68A6116E114FF3E015D0DF8E2167D67A3710FD5806285C5A44E4E15C51EB62'then raise_application_error(-20886,'SOURCE_GUARD_RRL_INVENTORY_TASK_ACCESS');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_INVENTORY_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='84982C5FB169AF20A35537AD1FCA41665139F35E449CD0BEA7545F534AD8A94A'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_INVENTORY_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_SHORT_RECOVERY'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='9EFF8820E1D4FC593B95C66B7AC2DB4B2932CECE133A0FE4056326185F662028'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_SHORT_RECOVERY');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_SHORT_RECOVERY'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='3DE0926683E599905794AC032573727B758B4FDD29AE30722E903CDBD46FD856'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_SHORT_RECOVERY');end if;dbms_lob.freetemporary(a);
end;
/
