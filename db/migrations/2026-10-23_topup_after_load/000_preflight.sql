declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 same('RRL_TRADE_TOPUP_READ','PACKAGE','2904D679E038FAB7FDF31A36F80FE03665E9AD97B9B93A1ED09ED322EC61AD60','SOURCE_DRIFT');
 same('RRL_TRADE_TOPUP_READ','PACKAGE BODY','FA3BFC05C765A276E6653FB0F7D20537640F3AAF8A072D1AF0E9FC82C1F468FB','SOURCE_DRIFT');
 same('RRL_TRADE_TOPUP_API','PACKAGE BODY','1B2A60FD3A362E7865D6E368D20D7404D6CDFE0D93F4F05932EADB4B99F6C17B','SOURCE_DRIFT');
 same('RRL_TRADE_TOPUP_CMD','PACKAGE BODY','B5C54B308B3A3D97149FA40E36E93A2CD68E54DA35FA6C1D60856278CA6051F1','SOURCE_DRIFT');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;
end;
/
