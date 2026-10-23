declare s clob;n number;begin
 dbms_lob.createtemporary(s,true);
 for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_PICK_CMD'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
 if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'528383B6901231C39FF47D1BCAD2BC35E778E3A0F1A268ABE9F9CBF3FA000489' then raise_application_error(-20999,'ROLLBACK_SOURCE_MISMATCH');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_CASE_PICK_PAPER';if n<>0 then raise_application_error(-20999,'CASE_PAPER_REMAINS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
