declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_RESOURCE_POLICY'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D97BF859C9F5BCB5A62E6AA473DF40F2410B1E54588D5374CDE09C3DF4E01B89'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_RESOURCE_POLICY');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_TASK_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='77A708C1475DE798D7C5F66D5F5F245ADB55E9A278BA7048045C5183A28E4CD9'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_TASK_ACCESS');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_TRANSFER_SCOPE'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='43CEA533BECFEA25147E8195F33570A3C10C0EBB78385351F9E68B1626A938B0'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_TRANSFER_SCOPE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_TRANSFER_SCOPE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='26A7545F3BD56FEF1B5837AE2CA792B7D6BE88B847E34F4A93259AAB6E5F887B'then raise_application_error(-20886,'SOURCE_GUARD_RRL_CASE_TRANSFER_SCOPE');end if;dbms_lob.freetemporary(a);
end;
/
