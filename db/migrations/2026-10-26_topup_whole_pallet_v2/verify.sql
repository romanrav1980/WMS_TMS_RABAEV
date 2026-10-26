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
 same('RRL_PICKING_API','PACKAGE BODY','242BD8D6FA3AB6542B426AB1C7C2AF69375017FA79F8E1F56893287E0DDFD8A2');
 same('RRL_PICKING_API','PACKAGE','141A8E6781BDE8626077FB8881FCF1FFF1BED0B2705318A0BA5A2A082AE9EB8C');
 same('RRL_TRADE_TOPUP_ADOPT','PACKAGE BODY','8AA8EBBAA8C2BE720B7ABD6D78106E128F0213E1F2E12D378629BB73D2AD454A');
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;select count(*)into n from USER_ERRORS where NAME='RRL_PICKING_API'and ATTRIBUTE='ERROR';if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;end;
/
