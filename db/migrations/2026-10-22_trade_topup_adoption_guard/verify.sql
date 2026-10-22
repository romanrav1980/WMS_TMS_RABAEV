declare s clob;n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 dbms_lob.createtemporary(s,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_RESERVATION_GUARD' and TYPE='TRIGGER' order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'2662506FC91C262BDDDD92BF4FF3C2D7FB873D7BD6C4DA151CC7B1F1205585B4'then raise_application_error(-20999,'RESERVATION_GUARD_SOURCE_DRIFT');end if;
 dbms_lob.freetemporary(s);
 select count(*)into n from USER_OBJECTS where STATUS='INVALID' and OBJECT_NAME not like 'BIN$%';
 if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
