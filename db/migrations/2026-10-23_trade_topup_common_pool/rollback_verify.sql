declare s clob;n number;
 procedure same(p_name varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_STOCK_POOL_READ','3C4BE33AD22ACCC12CCD4E4157A66508F7FC4914C04C3C94CB3577C23E29BE3B','ROLLBACK_SOURCE_MISMATCH');
 same('RRL_STOCK_POOL_CMD','35BFECEC73FB5D0CB4C7041D9D05623BA6079D0044899B86C0CAF78889F0A477','ROLLBACK_SOURCE_MISMATCH');
 same('RRL_TRADE_TOPUP_ADOPT','94B1F0CF2C0B5F693A3BF6E7CF75B56343850576DD27B8588730A28FC085E294','ROLLBACK_SOURCE_MISMATCH');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
