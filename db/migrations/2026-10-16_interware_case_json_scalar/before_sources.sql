declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_IW_CASE_BRIDGE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='3188C9A17D7A6A3D296D3E1AB7B0707FC441A169DEF5CE539E19E3777F1D1161'then raise_application_error(-20886,'SOURCE_GUARD_RRL_IW_CASE_BRIDGE');end if;dbms_lob.freetemporary(a);
end;
/
