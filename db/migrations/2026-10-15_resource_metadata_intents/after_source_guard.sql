declare n number;a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_RESOURCE_INTENT_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or upper(rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256)))!='FD0D00A6A92C0E3C95B2897E3C9EF098901CCE864AA2C6142583EEE433553027'then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_RRL_RESOURCE_INTENT_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_RESOURCE_INTENT_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or upper(rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256)))!='8C7E02857A46AD53541E3A3E8ED5515772E2C30DC9E19616919E251666BA4C8F'then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_RRL_RESOURCE_INTENT_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_RESOURCE_INTENT_GUARD'and TYPE='TRIGGER'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or upper(rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256)))!='8B8F6744C8FD5BDF1369ED3ACDC4D92366205552C7E0072C56A621B1DF378613'then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_RRL_RESOURCE_INTENT_GUARD');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_ASSIGNMENT_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or upper(rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256)))!='94FCDB300BA0A20EB7D9292A22971DEEB4ABC2D3411889B1449713B107F695A8'then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_RRL_CASE_ASSIGNMENT_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_ASSIGNMENT_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or upper(rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256)))!='17A13DC2439099F91CC0BF9207171609F5C15D76D704C8C3465A34018B48545B'then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_RRL_CASE_ASSIGNMENT_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WTASK_ASSIGN_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or upper(rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256)))!='23BD19364FA343539D391AA9757B4D4ABE57B387960C7EF587948C29E78A1D2E'then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_RRL_WTASK_ASSIGN_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WTASK_ASSIGN_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or upper(rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256)))!='CC331ABBE38B775069FF9355B5A5E8063196EF0409CEC017B4D2C84E9EE24D7D'then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_RRL_WTASK_ASSIGN_API');end if;dbms_lob.freetemporary(a);
end;
/
