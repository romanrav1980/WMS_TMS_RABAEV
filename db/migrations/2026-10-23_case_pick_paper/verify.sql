declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,'AFTER_SOURCE_MISMATCH:'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_CASE_PICK_PAPER','RRL_STOCK_CASE_PICK_CMD');if n<>0 then raise_application_error(-20999,'CASE_PAPER_COMPILE_ERRORS');end if;
 same('RRL_STOCK_CASE_PICK_CMD','PACKAGE BODY','53EA97ECEF44BC34CEBEAC464F6A131D0F31D51A3C27221CB2715740485E735F');
 same('RRL_CASE_PICK_PAPER','PACKAGE','CFA6B9FF605C009EC8960270808152865A809D4675CB73DEB153CF60591BD688');
 same('RRL_CASE_PICK_PAPER','PACKAGE BODY','E7B8B94A53DEBC472A6B28D3423D957BC838745362969FA14A86FFBE4C3CE6CD');
end;
/
