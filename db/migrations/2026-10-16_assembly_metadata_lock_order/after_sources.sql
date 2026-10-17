declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_ASM_META_SCOPE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='BB4E8CDAD45C5270601CB9F0BFB16699DA06313C53C32A347613C6ACE9340326'then raise_application_error(-20886,'ASM_ORDER_SOURCE_RRL_ASM_META_SCOPE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_ASSEMBLY_SCALE_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='B71DF7482ECE70AB3E9108CA47E9C86CBFAB08CA2642505E523A238BC9EC5A35'then raise_application_error(-20886,'ASM_ORDER_SOURCE_RRL_ASSEMBLY_SCALE_API');end if;dbms_lob.freetemporary(a);
end;
/
