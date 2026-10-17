declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_TASK_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='6DBEAE26DBFA93C18987333EA920D5F3054CD8989E152B871D2C43D3BAE369FD'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_TASK_ACCESS');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_RETURN_CMD'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='3833CF8B8493BFC499A4B13AE182F441A34E075949C5FE526247EF5FF9B7FBBC'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_CASE_RETURN_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_RETURN_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='BA4F3CB4B3AA0A6204BD51465573E44849FD72279D77563C586962944D762AB4'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_CASE_RETURN_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_WAVE_FINISH_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='891E1D4997C30BE04CC465CBEB072718EA247FF7AC43A1349BC424F1859E303F'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_WAVE_FINISH_CMD');end if;dbms_lob.freetemporary(a);
end;
/
