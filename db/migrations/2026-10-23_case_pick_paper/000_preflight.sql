declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,'SOURCE_DRIFT:'||p_name);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 same('RRL_STOCK_CASE_PICK_CMD','PACKAGE BODY','528383B6901231C39FF47D1BCAD2BC35E778E3A0F1A268ABE9F9CBF3FA000489');
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_CASE_PICK_PAPER';if n<>0 then raise_application_error(-20999,'CASE_PAPER_ALREADY_PRESENT');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;
end;
/
