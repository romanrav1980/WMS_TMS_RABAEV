whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
declare s clob;
 procedure same(n varchar2,t varchar2,h varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=n and TYPE=t order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>h then raise_application_error(-20999,'SOURCE_OR_DEPENDENCY_DRIFT'||':'||n||':'||t);end if;
  dbms_lob.freetemporary(s);
 end;
 begin
 same('RRL_STOCK_LOCK_API','PACKAGE BODY','CE59F19D781CF4953B852788D83732D56C7ADB321C49A805D33CEBB99555ABB2');
 same('RRL_STOCK_LOCK_API','PACKAGE','5E65D9B3D4B3FB367EE698B72709BF4FD396EDF2177156D73A7EB7ECF787ACD4');
 same('RRL_STOCK_POSTING_API','PACKAGE BODY','EB97721019B0177F4077C6DF224F3707D10F51DAFCD104EF0EE78D83FE56FA48');
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;select count(*)into n from USER_ERRORS where NAME='RRL_STOCK_LOCK_API'and ATTRIBUTE='ERROR';if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;end;
/
