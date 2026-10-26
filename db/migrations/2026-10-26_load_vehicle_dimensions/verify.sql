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
 same('RRL_STOCK_HU_LOAD_CORE','PACKAGE BODY','88E56C00FBCD1A5E87896927597F8F6F5EB937C30EBF3F2F9EB264E396084221');
 same('RRL_STOCK_HU_LOAD_CORE','PACKAGE','5F712EAE3DD0DC90527110FFBFCE9BC327BD18B15008FE3864868FD23E930A32');
 same('RRL_VEHICLE_PROFILE_API','PACKAGE BODY','68E01C228A98FB914A21A2B3C8727FA9E2DBA83AC392B532584A45276736407A');
 same('RRL_STOCK_LOAD_FLOOR','PACKAGE BODY','E666F1BE35E646A5021C2337B27B244FDC1FD6767C638F811FA9FCCDD58D4EC0');
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;select count(*)into n from USER_ERRORS where NAME='RRL_STOCK_HU_LOAD_CORE'and ATTRIBUTE='ERROR';if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;end;
/
