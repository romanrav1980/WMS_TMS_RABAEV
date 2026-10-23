declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_YARD_VISIT_API','PACKAGE','FF8BFA09875F6E47F9DCF54442D5DF732994D613480B234CFFDA1F0198B20EB3','AFTER_SOURCE_MISMATCH');
 same('RRL_YARD_VISIT_API','PACKAGE BODY','400EAF0A207CA3F2683642BA3EF3597E40A2E25351F2A4DCA5FB2ADEBBD523DB','AFTER_SOURCE_MISMATCH');
 same('RRL_YARD_DOCK_PLAN_API','PACKAGE','BECD3CD395011A915DD2E34BE1C386BB2B48F3788A04119F5594A64C1AD8A5E6','AFTER_SOURCE_MISMATCH');
 same('RRL_YARD_DOCK_PLAN_API','PACKAGE BODY','002C1C1326BE53B74BCAAA8723CE17D97563D5CF784918ECC259A2F26FA17D39','AFTER_SOURCE_MISMATCH');
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_YARD_DOCK_PLAN','RRL_YARD_DOCK_PLAN_EVENT','RRL_YARD_DOCK_PLAN_SQ','RRL_YARD_DOCK_PLAN_API','RRL_YARD_DOCK_PLAN_EVENT_APPEND');if n<5 then raise_application_error(-20999,'DOCK_PLAN_OBJECT_MISSING');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_YARD_VISIT_API','RRL_YARD_DOCK_PLAN_API','RRL_YARD_DOCK_PLAN_EVENT_APPEND');if n<>0 then raise_application_error(-20999,'COMPILE_ERRORS');end if;
end;
/
