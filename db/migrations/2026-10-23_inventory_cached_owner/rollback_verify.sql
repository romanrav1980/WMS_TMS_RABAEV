declare s clob;n number;
 procedure same(p_name varchar2,p_type varchar2,p_hash varchar2)is begin
  dbms_lob.createtemporary(s,true);
  for r in(select TEXT from USER_SOURCE where NAME=p_name and TYPE=p_type order by LINE)loop dbms_lob.append(s,replace(r.TEXT,chr(13),''));end loop;
  if dbms_lob.getlength(s)=0 or rawtohex(sys.dbms_crypto.hash(rtrim(s,chr(10)),sys.dbms_crypto.hash_sh256))<>p_hash then raise_application_error(-20999,'SOURCE_MISMATCH:'||p_name||':'||p_type);end if;
  dbms_lob.freetemporary(s);
 end;
begin
 same('RRL_TRADE_STOCK_GUARD','PACKAGE','555A92C50609C9198308AE1E4129AECCB34E891ADC14170F016B739596B447AA');
 same('RRL_STOCK_INVENTORY_CMD','PACKAGE BODY','F491ED14050AAEAFC33A010223CCA9ADE49A6CD78C72260513A9CC5675FBBD07');
 same('RRL_STOCK_UNIT_CORE','PACKAGE','98087FB04676531BB24BB84557244168315BF23638B7FB5C671AEA7A47FE4E03');
 same('RRL_STOCK_UNIT_CORE','PACKAGE BODY','DD03550CF5A185F4A513E233D1FA2BE55EB7764435129EB6FB62CEB8E3434E65');
 same('RRL_TRADE_STOCK_GUARD','PACKAGE BODY','7D6E1781DB7F46AC66105865B83D583C2FF35A9A905C1D8B91C97421CF0A68EE');
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
