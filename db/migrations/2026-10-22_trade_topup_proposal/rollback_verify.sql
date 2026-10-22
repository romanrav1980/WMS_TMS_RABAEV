declare s clob;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,'SOURCE_NOT_RESTORED:'||p_name);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 same('RRL_STOCK_POSTING_API','PACKAGE BODY','91105E27D0C094DEF62BC863C4C134419DBDF7A8022805004E32C3C892CC397A');
 same('RRL_TRADE_STOCK_GUARD','PACKAGE BODY','3B35292E0E15690F42ED557AF91A615590BF2A3BA9E62D1AC16C03F21893B1BA');
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE BODY','A294ADC710D6FD3B3C38A326F5EB192CB49D2F71CF2AA5E17EE3B76258408874');
 same('RRL_STOCK_RESERVE_CORE','PACKAGE','DC186B1AB40864265BA3C079BB703572E61E0B808E83CB45C762BE6E3EFD660E');
 same('RRL_STOCK_UNIT_CORE','PACKAGE','AAD653FD39181180E49B58A56E8D1CDFBFEC645BDED01C75E3BC604864B0DF0E');
end;
/
declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TRADE_TOPUP_READ','RRL_TRADE_TOPUP_API','RRL_TRADE_TOPUP_CMD','RRL_TRADE_TOPUP_EVENT','RRL_TRADE_TOPUP_HOLD','RRL_TRADE_TOPUP_DECISION','RRL_TRADE_TOPUP_PROPOSAL','RRL_TRADE_TOPUP_PROPOSAL_SQ');
 if n<>0 then raise_application_error(-20999,'TOPUP_OBJECTS_REMAIN');end if;
end;
/
