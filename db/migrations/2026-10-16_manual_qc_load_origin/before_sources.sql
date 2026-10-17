declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOAD_BOX_CORE'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='35F1F62CA5DF979753EABF446DE73AD5AE84B466BD25270E00680BE2BD382849'then raise_application_error(-20886,'SOURCE_GUARD_RRL_STOCK_LOAD_BOX_CORE');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TT_LOAD_BOX_WEIGHT_GUARD'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='D0CA66F6FB74E9F2E954C1B0A967CAC6A85C14E61CFA64FE3B76BA41E129A3ED'then raise_application_error(-20886,'SOURCE_GUARD_RRL_TT_LOAD_BOX_WEIGHT_GUARD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WH_FINAL_SCALE_ADMISSION'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='93E841F273784E5A4EF90A42C6A498C9A0278299C4DD0A05A8CFB2931A99BED2'then raise_application_error(-20886,'SOURCE_GUARD_RRL_WH_FINAL_SCALE_ADMISSION');end if;dbms_lob.freetemporary(a);
end;
/
