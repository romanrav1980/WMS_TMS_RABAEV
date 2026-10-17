declare a clob;n number;begin
 dbms_lob.createtemporary(a,true);
 for s in(select TEXT from USER_SOURCE where NAME='RRL_ASSEMBLY_SCALE_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(s.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='0D8C29AF78DC7564DFD86DE944ADEE4313AFEBE46E385324F4BDBADDD23A52AB'then raise_application_error(-20886,'ASM_INTENT_FRESH_SOURCE_MISMATCH');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME like 'RRL_ASM_INTENT%';if n!=0 then raise_application_error(-20886,'ASM_INTENT_NAMESPACE_NOT_EMPTY');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'ASM_INTENT_INVALID_BEFORE');end if;
end;
/
