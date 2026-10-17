declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TASK_RESOURCE_POLICY'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='A021B05B9F426686DA0510FEC1CB36E1DB62DC32AC42F1AB734C64C0E8E948CD'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TASK_RESOURCE_POLICY');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WAREHOUSE_TASK_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='604DAB919C40EDA35DC7B73C4F2DC7C98B70EE5F9237AEEBEA54861E978C099B'then raise_application_error(-20886,'SOURCE_GUARD_RRL_WAREHOUSE_TASK_ACCESS');end if;dbms_lob.freetemporary(a);
end;
/
