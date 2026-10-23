declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE','5BDC69384693B91FBECE9A5242B75E9C545BE77BA665398B4267B427E2B3B0B7','SOURCE_DRIFT');
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE BODY','204D42072234011B1903806E97AA5279875C293AD6BB443ECD825A739EC3FC91','SOURCE_DRIFT');
 same('RRL_STOCK_POOL_READ','PACKAGE BODY','761B51CA2258159170DD40C50C988CAD6C1B706FE7577A31CD439C4A9DA126C1','SOURCE_DRIFT');
 same('RRL_STOCK_POOL_CMD','PACKAGE BODY','76AC3806FD7FF7C41D02B318D6A373694B3D364D36C7508C0162A6DE3621A6B3','SOURCE_DRIFT');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;
end;
/
