declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE','229656B24904B16A276E29F8C86609549A4F87BC7242556C258C89BD38500991','AFTER_SOURCE_MISMATCH');
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE BODY','F7733DEBAEC656E7C6919BF0B98280B0866069D0A4221016CC07DADC11A9405C','AFTER_SOURCE_MISMATCH');
 same('RRL_STOCK_POOL_READ','PACKAGE BODY','F101CD643359541ADB295A663FA9BE0747167B80B48BCA845829C2AB2D019258','AFTER_SOURCE_MISMATCH');
 same('RRL_STOCK_POOL_CMD','PACKAGE BODY','747454DA64658AA501E89EB897719E1956A326167CA76C71882AD3C32BC61661','AFTER_SOURCE_MISMATCH');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_TRADE_PICK_CONTEXT','RRL_STOCK_POOL_READ','RRL_STOCK_POOL_CMD');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;
end;
/
