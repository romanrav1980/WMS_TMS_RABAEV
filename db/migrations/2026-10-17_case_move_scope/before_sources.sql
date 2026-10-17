declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_MOVE_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D124FCC4E2D2AF9447AB3463907B1EEADB2A72596C9756ECA2EE3635FA9CF021'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_CASE_MOVE_CMD');end if;dbms_lob.freetemporary(a);
end;
/
