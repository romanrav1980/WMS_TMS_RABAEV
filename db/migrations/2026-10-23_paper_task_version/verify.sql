declare s clob;n number;begin
 if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_TASK'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'34D8A9F0490E22C5239C39BC772C423803E76E7450AC8A2A8CAB31B6F291E031'then raise_application_error(-20999,'PAPER_TASK_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(s);
 dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_MOVE_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'884DFDEF660533285D5857A3C518497384BEE33C9237C2D58AE052E43AFD8C83'then raise_application_error(-20999,'PAPER_TASK_SOURCE_MISMATCH');end if;dbms_lob.freetemporary(s);
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
