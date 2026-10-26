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
 same('RRL_STOCK_LOCK_API','PACKAGE BODY','47C7F2AEED9241558C7B192C0F4C5B54CBCAE4CF2E7E95AA35E19EA12457958E');
 same('RRL_STOCK_LOCK_API','PACKAGE','5E65D9B3D4B3FB367EE698B72709BF4FD396EDF2177156D73A7EB7ECF787ACD4');
 same('RRL_STOCK_POSTING_API','PACKAGE BODY','EB97721019B0177F4077C6DF224F3707D10F51DAFCD104EF0EE78D83FE56FA48');
 same('RRL_STOCK_WAVE_LAUNCH_CMD','PACKAGE BODY','BFD53F02A7B8EC4A031546A880006CCB83CC524BD34CD082535122BF3DE14E52');
 same('RRL_TRADE_QUALITY_CASE_API','PACKAGE BODY','D4945CE9947AFBB88E9AC3C54B0B4AA5C9E7E43DC11B8DA9E53B3B96BCD71031');
end;
/
