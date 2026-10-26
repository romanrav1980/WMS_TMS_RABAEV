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
 same('RRL_STOCK_TRIP_DEPART_CMD','PACKAGE BODY','DF7B384066875F3CB791E9999A0D51C5F42F8AD84B4FB5C5D41342D26548D5C8');
 same('RRL_STOCK_LOAD_FLOOR','PACKAGE BODY','05DC140AFEBB2956785B81EBD632EB8D67913B226A9633A53D7DEFA16FE00D0D');
end;
/
declare n number;begin select count(*)into n from user_objects where status='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;end;
/
