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
 same('RRL_SAP_PALLET_WRITE_GUARD','TRIGGER','8C241D735E161D67A8AA1E42A266F8591CFA645779E27031D44303F1EC764DFB');
 same('RRL_STOCK_TASK_PLAN','PACKAGE BODY','F860BD48AB59205FCE072A1E95E4192B1FF6783507C7938261B6F2F7E9AAF692');
 same('RRL_STOCK_TASK_CORE','PACKAGE BODY','F365252A78143CB361BA6A643C7D5579E4AB8CF00CF569ADFCE126991BF24F9C');
end;
/
