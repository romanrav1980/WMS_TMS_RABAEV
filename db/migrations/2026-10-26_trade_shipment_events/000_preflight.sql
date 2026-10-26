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
 same('RRL_STOCK_TRIP_DEPART_CMD','PACKAGE BODY','0BC5B3C7C13D6C4A403D2A84A6EF85D959AFCD8B76D12E316B713F9F5D43272F');
 same('RRL_STOCK_TRIP_DEPART_CMD','PACKAGE','9314F735ABF2D1C48C035EBB25EB9D8C25A83604FAC2546610744A8A6B0F3C64');
 same('RRL_STOCK_POSTING_API','PACKAGE BODY','EB97721019B0177F4077C6DF224F3707D10F51DAFCD104EF0EE78D83FE56FA48');
 same('RRL_TRADE_TRANSPORT_CORE','PACKAGE BODY','283127E6FB8931716D5B94DAF7656BC9D1FDD4AC1BF48191B20A5B9B4DEB52FE');
 same('RRL_TRADE_TRANSIT_PROOF','PACKAGE','AED1D8D486C4276FC1E6EF8171C3CCBE5A38F5BB97A9383E939BD6BEF55BFFAF');
 same('RRL_TRADE_TRANSIT_PROOF','PACKAGE BODY','DE0C5936CABA30532597147F781E3B106A93F6ED06FFA7D6010E3D222655CAAD');
 same('RRL_TRACEABILITY_API','PACKAGE BODY','4131765217B3C15BE5273A2539E238E5CA16C367311667D9FBBE1A8FDAE68196');
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_TRADE_SHIP_EVENT';if n<>0 then raise_application_error(-20999,'SHIP_EVENT_OBJECT_MUST_BE_ABSENT');end if;end;
/
