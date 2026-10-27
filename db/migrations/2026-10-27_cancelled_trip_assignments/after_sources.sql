declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_DOCUMENT_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='4B3423E4169309930DC4F54F88AE1373CBA41132B98F201DDCF8320B43B04670'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TRADE_DOCUMENT_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_DOCUMENT_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='72C71E5CA42066E07EC387DECA2CA74A3794926FC5558EB27F342E74179E193E'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TRADE_DOCUMENT_API');end if;dbms_lob.freetemporary(a);
end;
/
