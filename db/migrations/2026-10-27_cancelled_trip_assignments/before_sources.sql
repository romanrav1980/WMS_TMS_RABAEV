declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_DOCUMENT_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='4B3423E4169309930DC4F54F88AE1373CBA41132B98F201DDCF8320B43B04670'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TRADE_DOCUMENT_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_DOCUMENT_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='E4BB0683DCFA1C64A974B0ACEA2E7A01375FD1E1AA97A2F1E658D5105281B2B9'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TRADE_DOCUMENT_API');end if;dbms_lob.freetemporary(a);
end;
/
