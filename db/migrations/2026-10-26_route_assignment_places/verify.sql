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
 same('RRL_TRANSPORT_PLAN_API','PACKAGE BODY','6CDFAAD7F49F1770B82B79CA2F1A0042823E51310FA3B61B2422B164D324BBAA');
 same('RRL_TRANSPORT_PLAN_RULES','PACKAGE BODY','C78D40A6CE5DBCAE4DB03ABBE51B6963F871D0E0DBCEA6AA3EAD061602045E5B');
 same('RRL_TRANSPORT_PLAN_API','PACKAGE','CA927E2E73071EB85D3F18F77E53FCCDB241C79E87F5D5B413628820BB5D4C66');
 same('RRL_TRANSPORT_PLAN_RULES','PACKAGE','212B475C20AB28355BE92C48BE2DB97B2DAF61D19BFD75B0BADD8CA4E0B19302');
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;end;
/
