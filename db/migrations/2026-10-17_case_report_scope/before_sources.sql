declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_RESOURCE_POLICY'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D97BF859C9F5BCB5A62E6AA473DF40F2410B1E54588D5374CDE09C3DF4E01B89'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_RESOURCE_POLICY');end if;dbms_lob.freetemporary(a);
end;
/
