declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_TRADE_TOPUP_READ','PACKAGE','C1EC2E5464626E72760CA9AAA420B5D24EDA87DA063C5F40C3A7AD8A7FEE64EE','AFTER_SOURCE_MISMATCH');
 same('RRL_TRADE_TOPUP_READ','PACKAGE BODY','1483937FF45EE07E378739787580D2FED8EF9329C269146C3BE8064F17E75AEE','AFTER_SOURCE_MISMATCH');
 same('RRL_TRADE_TOPUP_API','PACKAGE BODY','90CA9D8A678E266A4C44E1569652ED75A1B710F9100280D9A2D9A58850653E0F','AFTER_SOURCE_MISMATCH');
 same('RRL_TRADE_TOPUP_CMD','PACKAGE BODY','2A6635FA57ED3108EC096E57E40A78D6A459BBB1B558FBB4DC817D0266CE0373','AFTER_SOURCE_MISMATCH');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_TRADE_TOPUP_READ','RRL_TRADE_TOPUP_API','RRL_TRADE_TOPUP_CMD');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;
end;
/
