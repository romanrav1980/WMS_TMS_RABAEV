declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_TRADE_STOCK_GUARD','PACKAGE BODY','B928B1CF69547F47065C95A3BBF99F35A3AA2C5B63327BAB19D8F36D8D5F22D9','AFTER_SOURCE_MISMATCH');
 same('RRL_TRADE_STOCK_GUARD','PACKAGE','555A92C50609C9198308AE1E4129AECCB34E891ADC14170F016B739596B447AA','DEPENDENCY_CHANGED');
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE','229656B24904B16A276E29F8C86609549A4F87BC7242556C258C89BD38500991','DEPENDENCY_CHANGED');
 same('RRL_STOCK_CASE_SHORT_CMD','PACKAGE BODY','52299F14EBB41C5CEB5C78B3D8EEB52726156247007D2F202D1BF017E068FAFA','DEPENDENCY_CHANGED');
 same('RRL_STOCK_SHORT_RECOVERY','PACKAGE BODY','F01F32A68888AB378C538E30CE4D5F7FE423ECF255B5886ACE8A78FFCF67285E','DEPENDENCY_CHANGED');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME='RRL_TRADE_STOCK_GUARD';if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;
end;
/
