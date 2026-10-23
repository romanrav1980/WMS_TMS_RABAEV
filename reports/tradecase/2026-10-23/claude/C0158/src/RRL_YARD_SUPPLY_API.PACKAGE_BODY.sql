package body RRL_YARD_SUPPLY_API as
 g_tx varchar2(100);
 function write_allowed return number is begin
  if g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure fail(p_code varchar2)is begin raise_application_error(-20911,p_code);end;
 function source_version(p_ware number,p_supply varchar2,p_actor varchar2,p_write number)return number is
  body clob;v number;owner_id varchar2(100);
 begin
  begin select BODY_JSON,VERSION_NO into body,v from RRL_TRADE_DOCUMENT
   where WARE_ID=p_ware and ENTITY_TYPE='SUPPLY'and EXTERNAL_ID=p_supply and STATUS='ACCEPTED'
   order by VERSION_NO desc fetch first 1 rows only;
  exception when no_data_found then fail('YARD_SUPPLY_NOT_FOUND');end;
  owner_id:=json_object_t.parse(body).get_string('owner_id');
  if owner_id is null or RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,p_ware,owner_id,0)<>1 then fail('YARD_SUPPLY_NOT_FOUND');end if;
  if p_write=1 then RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,owner_id,1);end if;
  return v;
 end;
 procedure check_request(p_ware number,p_sources clob,p_actor varchar2)is
  a json_array_t:=json_array_t.parse(p_sources);seen json_object_t:=json_object_t();id_value varchar2(100);v number;
 begin
  if a.get_size not between 1 and 200 then fail('YARD_SUPPLIES_REQUIRED');end if;
  for i in 0..a.get_size-1 loop
   id_value:=a.get_string(i);
   if trim(id_value)is null or seen.has(id_value)then fail('YARD_REQUEST_INVALID');end if;
   seen.put(id_value,true);v:=source_version(p_ware,id_value,p_actor,1);
  end loop;
 end;
 procedure create_links(p_ware number,p_visit number,p_sources clob,p_actor varchar2)is
  a json_array_t:=json_array_t.parse(p_sources);id_value varchar2(100);v number;n number;
 begin
  check_request(p_ware,p_sources,p_actor);
  select count(*)into n from RRL_YARD_VISIT where VISIT_ID=p_visit and WARE_ID=p_ware and VISIT_KIND='INBOUND';
  if n<>1 then fail('YARD_VISIT_NOT_FOUND');end if;
  for i in 0..a.get_size-1 loop
   id_value:=a.get_string(i);v:=source_version(p_ware,id_value,p_actor,1);
   select count(*)into n from RRL_YARD_VISIT_SUPPLY s join RRL_YARD_VISIT y on y.VISIT_ID=s.VISIT_ID
    where s.WARE_ID=p_ware and s.SUPPLY_ID=id_value and y.STATE not in('DEPARTED','CANCELLED');
   if n<>0 then fail('YARD_SUPPLY_VISIT_ACTIVE');end if;
   g_tx:=dbms_transaction.local_transaction_id(true);
   insert into RRL_YARD_VISIT_SUPPLY(VISIT_ID,WARE_ID,SUPPLY_ID,DOCUMENT_VERSION)values(p_visit,p_ware,id_value,v);
   g_tx:=null;
  end loop;
 exception when others then g_tx:=null;raise;
 end;
 procedure assert_visit(p_ware number,p_visit number,p_actor varchar2,p_write number,p_frozen number default 0)is n number:=0;v number;
 begin
  for s in(select SUPPLY_ID,DOCUMENT_VERSION from RRL_YARD_VISIT_SUPPLY where VISIT_ID=p_visit and WARE_ID=p_ware order by SUPPLY_ID)loop
   n:=n+1;if n>200 then fail('YARD_SUPPLY_BOUND');end if;
   v:=source_version(p_ware,s.SUPPLY_ID,p_actor,p_write);
   if p_frozen=1 and v<>s.DOCUMENT_VERSION then fail('YARD_SUPPLY_CHANGED');end if;
  end loop;
  if n=0 then fail('YARD_SUPPLY_NOT_FOUND');end if;
 end;
 function supply_ids(p_visit number)return clob is a json_array_t:=json_array_t();n number:=0;
 begin
  for s in(select SUPPLY_ID from RRL_YARD_VISIT_SUPPLY where VISIT_ID=p_visit order by SUPPLY_ID)loop
   n:=n+1;if n>200 then fail('YARD_SUPPLY_BOUND');end if;a.append(s.SUPPLY_ID);
  end loop;return a.to_clob;
 end;
end;