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
 same('RRL_STOCK_INVARIANT_CORE','PACKAGE BODY','AA0EC81F1FEACF3B5E75570E28B01A2AE5460A98827049BE165B35D6589E9783');
 same('RRL_STOCK_INVARIANT_CORE','PACKAGE','0732A938FB2A9F0980832690014652874FAF3DB5B00D54643FBF559AB0FDC0CA');
 same('RRL_STOCK_POSTING_API','PACKAGE BODY','EB97721019B0177F4077C6DF224F3707D10F51DAFCD104EF0EE78D83FE56FA48');
 same('RRL_STOCK_UNIT_CORE','PACKAGE BODY','DD03550CF5A185F4A513E233D1FA2BE55EB7764435129EB6FB62CEB8E3434E65');
 same('RRL_TRADE_STOCK_GUARD','PACKAGE BODY','E72348D2921BA0E20908C575877AB5E0A7BF40467BF353572E94D8DFF0992AA1');
 same('RRL_STOCK_LOCK_API','PACKAGE BODY','8024DEB89407AC16945601431A0FD755F6EC07E30A77D53A019FE4D03BA59050');
end;
/
declare n number;begin select count(*)into n from user_objects where status='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;end;
/
declare n number;begin select count(*)into n from user_indexes where INDEX_NAME='RRL_UNIT_CELL_GUARD_IX';if n!=0 then raise_application_error(-20999,'INDEX_NOT_REMOVED');end if;end;
/
