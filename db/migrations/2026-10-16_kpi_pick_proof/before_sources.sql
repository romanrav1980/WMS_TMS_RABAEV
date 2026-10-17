declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_PICK_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='19CD9C4577ACD00E97C27E5A7F3292112747FD4E05B792B6041DC27755B146ED'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_CASE_PICK_CMD');end if;dbms_lob.freetemporary(a);
end;
/
