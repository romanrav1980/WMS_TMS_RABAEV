-- Additive reviewed v2 gate: UTF8 no BOM; exclude only BIN$ recycle-bin diagnostics.
declare n number;a clob;begin
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_ASSIGNMENT_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or upper(rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256)))!='6DFB49A0F85CFFA23D687DA6326A9F261707DE8DF61AE33B6AFCD5736657DE2A'then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_RRL_CASE_ASSIGNMENT_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_CASE_ASSIGNMENT_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or upper(rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256)))!='B8BD28CBBF821CC3872079AFDC60773C3EAF952DB6F2D223369BA35831420644'then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_RRL_CASE_ASSIGNMENT_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WTASK_ASSIGN_API'and TYPE='PACKAGE'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or upper(rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256)))!='E44625E5D3D047FE94EDA51BD4F67279DD2CE220C6F0E1576A0EAE432C11C698'then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_RRL_WTASK_ASSIGN_API');end if;dbms_lob.freetemporary(a);
 dbms_lob.createtemporary(a,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_WTASK_ASSIGN_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(a,replace(r.TEXT,chr(13),''));end loop;
 if dbms_lob.getlength(a)=0 or upper(rawtohex(sys.dbms_crypto.hash(a,sys.dbms_crypto.hash_sh256)))!='E67191F572B756B63A28CAEC0AE23C60AD3FC16F98CBC0C0E125AE7A190A753F'then raise_application_error(-20886,'RESOURCE_INTENT_SOURCE_RRL_WTASK_ASSIGN_API');end if;dbms_lob.freetemporary(a);
end;
/
declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_RESOURCE_INTENT_API','RRL_RESOURCE_INTENT_GUARD','RRL_RESOURCE_INTENT_ABANDON')or STATUS='INVALID';if n!=0 then raise_application_error(-20886,'RESOURCE_INTENT_ROLLBACK_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'RESOURCE_INTENT_ROLLBACK_ERRORS');end if;
end;
/
