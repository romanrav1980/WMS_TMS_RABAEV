declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_TOPUP_READ'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='5987C010916C9691A9FA2F8DED68311547E19CE338DD4CFAF0B2CBFCBDBD3C72'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TRADE_TOPUP_READ');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_TOPUP_READ'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='262D48C95844795FA4F94BC5D32E59F87A3230E4C0E99BBEA043CC4F3D795B09'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TRADE_TOPUP_READ');end if;dbms_lob.freetemporary(a);
end;
/
