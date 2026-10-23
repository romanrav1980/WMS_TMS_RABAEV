declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2,p_code varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,p_code||':'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_STOCK_POOL_CMD','PACKAGE','E1091C7662A9EFBE69E56CD6FF99CD783945B56C8F1B1CC75EC449DBE6DE57D9','ROLLBACK_SOURCE_MISMATCH');
 same('RRL_STOCK_POOL_CMD','PACKAGE BODY','4ABD6C109C87870EF6D042B1F03D25FE7A60F64E7E58EB4A39DA1C45F4DE796F','ROLLBACK_SOURCE_MISMATCH');
 same('RRL_STOCK_POSTING_API','PACKAGE BODY','6DAA16DD11152C696B6B20D5E10247BF59F36D2E94BB08489402516D0082BC81','ROLLBACK_SOURCE_MISMATCH');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
