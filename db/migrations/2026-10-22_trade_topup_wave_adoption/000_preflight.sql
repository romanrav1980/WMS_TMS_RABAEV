declare s clob;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,'SOURCE_DRIFT:'||p_name);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 same('RRL_STOCK_RESERVE_CORE','PACKAGE','5804CF404AE2F236EFD8844471F43BDD8B291C17698968C67A724738910E41A5');
 same('RRL_STOCK_RESERVE_CORE','PACKAGE BODY','A8F78A36E9340EF655FDE3E9CCDD80FA977089898F869B1DAD1B4060468648DC');
 same('RRL_PICKING_API','PACKAGE BODY','4F5A526F40D7DD4043413DD34616E210955CD139423C0899B57C7B48A45F6342');
 same('RRL_STOCK_WAVE_LAUNCH_CMD','PACKAGE BODY','73D6185313C59CCA2609FF24DBABB24441789C33E83A79328E711A855C9768E1');
 same('RRL_TRADE_PICK_CONTEXT','PACKAGE BODY','E88CB4256EFA8DB7EDB12C83CF4707F442E48A34DF241CD9E059431ECC423E6E');
end;
/
declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TRADE_TOPUP_ADOPT','RRL_TRADE_TOPUP_ADOPTION');
 if n<>0 then raise_application_error(-20999,'ADOPTION_OBJECTS_ALREADY_PRESENT');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;
end;
/
