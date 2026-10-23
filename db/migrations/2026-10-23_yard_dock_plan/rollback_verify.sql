declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_YARD_VISIT_API','PACKAGE','1BD9DF2572541AE6FB058DA42D4E600B3D3579213894C35F4E05952BA306798A','ROLLBACK_SOURCE_MISMATCH');
 same('RRL_YARD_VISIT_API','PACKAGE BODY','C3FF494DB2DF2F6D5AAB8C87918537BD71D82EB6CDDB874E5D82E54D59E7EC84','ROLLBACK_SOURCE_MISMATCH');
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_YARD_DOCK_PLAN','RRL_YARD_DOCK_PLAN_EVENT','RRL_YARD_DOCK_PLAN_SQ','RRL_YARD_DOCK_PLAN_API','RRL_YARD_DOCK_PLAN_EVENT_APPEND');if n<>0 then raise_application_error(-20999,'DOCK_PLAN_OBJECT_REMAINS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
