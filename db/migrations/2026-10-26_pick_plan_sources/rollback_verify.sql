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
 same('RRL_PICK_PLAN_ADMISSION','PACKAGE BODY','E47708D8E30E95CC464711B18A6F7B43FB211C05708894C1E239FE3A937CCDC9');
 same('RRL_PICK_PLAN_ADMISSION','PACKAGE','46BAEBD86EE175EB911DFAB7D6190792388E0E1670E7493ADE2EA8811619D0B6');
 same('RRL_PICK_PLAN_CREATE_API','PACKAGE BODY','0D70F7441FBAA384622F4F780CCD8A721FA5A84F35DF865213BD9420640322C5');
 same('RRL_PICKING_API','PACKAGE BODY','242BD8D6FA3AB6542B426AB1C7C2AF69375017FA79F8E1F56893287E0DDFD8A2');
 same('RRL_STOCK_LOCK_API','PACKAGE BODY','6FF947384486B47B89084E8236F260E0AAC4133C02125144EBDBC0C1E0819054');
end;
/
declare n number;begin select count(*)into n from user_objects where status='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;end;
/
