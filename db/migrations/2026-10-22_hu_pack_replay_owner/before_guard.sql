declare s clob;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_HU_EXEC_ACCESS'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'514122AFC25CCFA2C60E79749D9FE1426BFBB381DB95501154DF64E6ED8675DE'then raise_application_error(-20999,'HU_EXEC_SOURCE_DRIFT');end if;dbms_lob.freetemporary(s);
end;
/
