create or replace package RRL_INTERWARE_DEPART_GATE authid definer as 
 function promises(p_trip number)return clob; 
 procedure assert_ready(p_promises clob); 
end;
/

create or replace package body RRL_INTERWARE_DEPART_GATE as 
 function promises(p_trip number)return clob is a json_array_t:=json_array_t();j json_object_t;n number;count_value number:=0; 
 begin 
  for p in(select candidate.OPERATION_ID from( 
   select OPERATION_ID from RRL_INTERWARE_PLAN where TARGET_TT_ID=p_trip 
   union select PLAN_OPERATION_ID from RRL_INTERWARE_DECISION where TARGET_TT_ID=p_trip 
  )candidate where RRL_INTERWARE_ROUTING.target_trip(candidate.OPERATION_ID)=p_trip order by candidate.OPERATION_ID fetch first 201 rows only)loop 
   RRL_INTERWARE_THERMAL.assert_release(p.OPERATION_ID);count_value:=count_value+1;if count_value>200 then raise_application_error(-20881,'INTERWARE_DEPART_PROMISE_BOUND_200');end if; 
   select count(*)into n from RRL_INTERWARE_RECEIPT r join RRL_INTERWARE_ONWARD_BIND b on b.RECEIPT_OPERATION_ID=r.OPERATION_ID join RRL_TT_HU_LOAD_ST m on m.SBORKA_PALLET_ID=b.ST_ID and m.ACTIVE_FLAG=1 join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID and o.STATE='APPLIED' where (r.EXPECTED_BASE_QTY is null or r.BASE_QTY=r.EXPECTED_BASE_QTY or exists(
 select 1 from RRL_INTERWARE_SHORTAGE_FACT fact join RRL_STOCK_OPERATION confirmed on confirmed.OPERATION_ID=fact.OPERATION_ID
 where fact.RECEIPT_OPERATION_ID=r.OPERATION_ID and confirmed.STATE='APPLIED'and confirmed.COMMAND_TYPE='INTERWARE_SHORTAGE_CONFIRM'
 and fact.SHORT_QTY+r.BASE_QTY=r.EXPECTED_BASE_QTY))and r.PLAN_OPERATION_ID=p.OPERATION_ID and l.TT_ID=p_trip and l.STATUS='LOADED'and l.ROOT_UID=r.ROOT_UID
 and RRL_STOCK_MATH.quantity(json_value(l.COMPOSITION_JSON,'$.nodes[0].quantity'))=r.BASE_QTY; 
   j:=json_object_t();j.put('plan_operation_id',p.OPERATION_ID);j.put('physically_loaded',n=1);a.append(j); 
  end loop; 
  return a.to_clob; 
 end; 
 procedure assert_ready(p_promises clob)is a json_array_t:=json_array_t.parse(p_promises);j json_object_t; 
 begin 
  for i in 0..a.get_size-1 loop j:=treat(a.get(i)as json_object_t);if not j.get_boolean('physically_loaded')then raise_application_error(-20886,'DEPART_EXPECTED_INTERWARE_CARGO_NOT_READY: '||j.get_string('plan_operation_id'));end if;end loop; 
 end; 
end;
/
