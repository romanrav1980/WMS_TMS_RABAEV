declare s clob;n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_TRADE_TOPUP_CMD' and TYPE='PACKAGE BODY' order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'B5C54B308B3A3D97149FA40E36E93A2CD68E54DA35FA6C1D60856278CA6051F1'then raise_application_error(-20999,'TOPUP_RECONCILE_SOURCE_DRIFT');end if;
 dbms_lob.freetemporary(s);
 select count(*)into n from USER_OBJECTS where STATUS='INVALID' and OBJECT_NAME not like 'BIN$%';
 if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
