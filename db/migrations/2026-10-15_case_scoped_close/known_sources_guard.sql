declare a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_TASK_ACCESS'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='8D1486C3D76223DBDFFE6DBB3BE66F2F79695BF1F20CB6E11A3926A3EA051958'then raise_application_error(-20886,'CASE_CLOSE_SOURCE_RRL_CASE_TASK_ACCESS');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_TASK_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='745B1CF148F11C0F3ADCBFCF4EA2CA41B817875601D4C1D5761ECE0D73813C8C'then raise_application_error(-20886,'CASE_CLOSE_SOURCE_RRL_CASE_TASK_ACCESS');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_METADATA_TX'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='2F15C928927113570FCFD4C09B947D783FF958E9F1EC1811595081C7C6A012F5'then raise_application_error(-20886,'CASE_CLOSE_SOURCE_RRL_STOCK_METADATA_TX');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_METADATA_TX'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='62A037D11B5E211C6342101264DB75A6ABCD2DA827D23269B81B815AB4A41F54'then raise_application_error(-20886,'CASE_CLOSE_SOURCE_RRL_STOCK_METADATA_TX');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_LOCK_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256))!='C82FDD123B634C92F380EFDBF1DDC43A02630B2AED1FC5D1A192C615D2362A55'then raise_application_error(-20886,'CASE_CLOSE_SOURCE_RRL_STOCK_LOCK_API');end if;dbms_lob.freetemporary(a);
end;
/
