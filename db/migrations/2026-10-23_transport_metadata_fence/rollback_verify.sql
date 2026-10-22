declare s clob;n number;procedure same(t varchar2,h varchar2)is begin dbms_lob.createtemporary(s,true);for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_METADATA_TX'and TYPE=t order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>h then raise_application_error(-20999,'TRANSPORT_METADATA_SOURCE_MISMATCH:'||t);end if;end;begin
 if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
same('PACKAGE','5C2226F476E4498AADE46494BC62F1C710AACB65BAACE563686A3A5C604ADBF2');
same('PACKAGE BODY','2DE37D9A1D086B03551D781A772625EF48195825971CE24602723BEBCAE04207');
select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;end;
/
