declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_STOCK_POOL_CMD','PACKAGE','769D85923F70ED3F013445588657B17140166FC526B88D988A7CBF8F2528F0C8','AFTER_SOURCE_MISMATCH');
 same('RRL_STOCK_POOL_CMD','PACKAGE BODY','5CB7000E457D8C5BF8D9BDA4BF820BA62F74DF243E1BDA2511E573EC74B62652','AFTER_SOURCE_MISMATCH');
 same('RRL_STOCK_POSTING_API','PACKAGE BODY','EB97721019B0177F4077C6DF224F3707D10F51DAFCD104EF0EE78D83FE56FA48','AFTER_SOURCE_MISMATCH');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_STOCK_POOL_CMD','RRL_STOCK_POSTING_API');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;
end;
/
