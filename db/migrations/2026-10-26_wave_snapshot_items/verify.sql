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
 same('RRL_STOCK_WAVE_FINISH_CMD','PACKAGE BODY','28B28B7EBF7F0DBF0BFAB3211491B673ABD51DFF39342BEDF34D4A642F70A65C');
 same('RRL_STOCK_WAVE_FINISH_CMD','PACKAGE','6095F51C74F2D942E97093BDAE3FA5ACD48491CD81AEC8E1676749B9923874F4');
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;end;
/
