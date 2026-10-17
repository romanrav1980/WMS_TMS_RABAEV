declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_TASK_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='5B122285074AFE3FAA0AE079317345632CB1E4DC5C02E17FC351EACDF9F44949'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_TASK_ACCESS');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_RETURN_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='640E3446B3E05301C4A65B77C0C5FC329529BCF509BD26838B72F43ABE308728'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_CASE_RETURN_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='E2935A1E007561BDD76CE9000461641B07F42DFFFC8C1176353E149F7D96950B'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_POSTING_API');end if;dbms_lob.freetemporary(a);
end;
/
