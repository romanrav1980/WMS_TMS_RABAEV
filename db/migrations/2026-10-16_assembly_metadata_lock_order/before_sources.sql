declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_ASM_META_SCOPE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='8782128E226B5A0BE5DAF0D193267255D64BFBA224DC595832285B06A65B2B94'then raise_application_error(-20886,'ASM_ORDER_SOURCE_RRL_ASM_META_SCOPE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_ASSEMBLY_SCALE_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='4E2E23DCC4A764E8D4A04B971655E5B9C30DB6306F692B083CC32DF9830F7368'then raise_application_error(-20886,'ASM_ORDER_SOURCE_RRL_ASSEMBLY_SCALE_API');end if;dbms_lob.freetemporary(a);
end;
/
