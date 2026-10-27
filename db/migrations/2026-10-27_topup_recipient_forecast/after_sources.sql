declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_TOPUP_CMD'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A83DB66F0ED86760C4246DF49BD8C13C81E699B380BD31959D84395CC918789F'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TRADE_TOPUP_CMD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_TOPUP_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='B591C1CCB67102FD5FBDE5F7AB4DB3628DC48AF7FC2DDFDD5969A22C55F3E025'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TRADE_TOPUP_CMD');end if;dbms_lob.freetemporary(a);
end;
/
