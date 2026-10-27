declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE BODY','F7733DEBAEC656E7C6919BF0B98280B0866069D0A4221016CC07DADC11A9405C','BEFORE_SOURCE_DRIFT');
 same('RRL_TRADE_TRANSPORT_CORE','PACKAGE BODY','E5645184312C84C0AAA9606FFFD6DE8C286AB0459D2F06565E0D098BBDA7DEA9','BEFORE_SOURCE_DRIFT');
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE','229656B24904B16A276E29F8C86609549A4F87BC7242556C258C89BD38500991','DEPENDENCY_DRIFT');
 same('RRL_TRADE_TRANSPORT_CORE','PACKAGE','5AE5D8EF7D7C2D990DA51A1C05888FA46B936A6C2B8CE69B5C9F3A961B7A9E4F','DEPENDENCY_DRIFT');
 same('RRL_TRADE_TOPUP_ADOPT','PACKAGE','F6B49EA58218A622A2C77CFF9E958258AA5E8B007048055137730260D2CF6C8B','DEPENDENCY_DRIFT');
 same('RRL_TRADE_STOCK_GUARD','PACKAGE','555A92C50609C9198308AE1E4129AECCB34E891ADC14170F016B739596B447AA','DEPENDENCY_DRIFT');
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_TRADE_RECIPIENT_VERSION';if n<>0 then raise_application_error(-20999,'FUNCTION_ALREADY_EXISTS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;
end;
/
