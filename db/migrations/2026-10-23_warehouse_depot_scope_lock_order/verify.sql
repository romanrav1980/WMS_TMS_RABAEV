declare s clob;n number;begin
if user<>'RABAEV'or sys_context('USERENV','SERVICE_NAME')<>'orcl'then raise_application_error(-20999,'WRONG_TARGET');end if;
dbms_lob.createtemporary(s,true);
for r in(select TEXT from USER_SOURCE where NAME='RRL_STOCK_METADATA_TX'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'2DE37D9A1D086B03551D781A772625EF48195825971CE24602723BEBCAE04207'then raise_application_error(-20999,'DEPOT_SCOPE_SOURCE_DRIFT');end if;
dbms_lob.freetemporary(s);
dbms_lob.createtemporary(s,true);
for r in(select TEXT from USER_SOURCE where NAME='RRL_WARE_DEPOT_API'and TYPE='PACKAGE BODY'order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
if rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>'A72CF43B928DC28B539CBA44D0D6C12EDEB81C41263F099C8002267ADA7440C0'then raise_application_error(-20999,'DEPOT_SCOPE_SOURCE_DRIFT');end if;
dbms_lob.freetemporary(s);
select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
