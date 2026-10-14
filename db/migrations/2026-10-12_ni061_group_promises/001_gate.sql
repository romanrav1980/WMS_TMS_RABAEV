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
 and fact.SHORT_QTY+r.BASE_QTY=r.EXPECTED_BASE_QTY))and r.PLAN_OPERATION_ID=p.OPERATION_ID and l.TT_ID=p_trip and l.STATUS='LOADED'and(
 (l.ROOT_UID=r.ROOT_UID and RRL_STOCK_MATH.quantity(json_value(l.COMPOSITION_JSON,'$.nodes[0].quantity'))=r.BASE_QTY)
 or(o.COMMAND_TYPE='HU_SHIP'and l.ROOT_UID!=r.ROOT_UID
 and json_value(o.RESOLVED_PLAN_JSON,'$.domain.loading.trip'returning number)=p_trip
 and exists(select 1 from RRL_INTERWARE_ONWARD_DISPATCH dispatch where dispatch.OPERATION_ID=l.LOAD_OPERATION_ID
  and dispatch.BIND_OPERATION_ID=b.OPERATION_ID and dispatch.RECEIPT_OPERATION_ID=r.OPERATION_ID
  and dispatch.ROOT_UID=r.ROOT_UID and dispatch.ST_ID=b.ST_ID and dispatch.BASE_QTY=r.BASE_QTY and dispatch.BASE_UOM=r.BASE_UOM)
 and(select count(*)from json_table(l.COMPOSITION_JSON,'$.nodes[*]'columns(
  K varchar2(20)path '$.kind',U varchar2(200)path '$.uid',Q varchar2(60)path '$.quantity'))archive
  where archive.K='STOCK'and archive.U=r.ROOT_UID and RRL_STOCK_MATH.quantity(archive.Q)=r.BASE_QTY)=1))
;  
   j:=json_object_t();j.put('plan_operation_id',p.OPERATION_ID);j.put('physically_loaded',n=1);a.append(j);  
  end loop;  
  for gp in(select OPERATION_ID,SOURCE_JSON from RRL_IW_GROUP_PLAN where TARGET_TT_ID=p_trip order by OPERATION_ID fetch first 201 rows only)loop
   count_value:=count_value+1;if count_value>200 then raise_application_error(-20881,'INTERWARE_DEPART_PROMISE_BOUND_200');end if;
   select count(*)into n from json_table(gp.SOURCE_JSON,'$.lots[*]'columns(SOURCE_UID varchar2(200)path '$.uid',SOURCE_QTY varchar2(60)path '$.quantity',SOURCE_UOM varchar2(20)path '$.base_uom'))expected
   where not exists(
    select 1 from RRL_TT_HU_LOAD_FACT lf join RRL_STOCK_OPERATION o on o.OPERATION_ID=lf.LOAD_OPERATION_ID and o.STATE='APPLIED'
    join json_table(o.RESOLVED_PLAN_JSON,'$.domain.shipments[*]'columns(
     GROUP_PLAN varchar2(100)path '$.domain.interwarehouse_onward_source.group_plan_operation_id',
     LOT_UID varchar2(200)path '$.domain.interwarehouse_onward_source.uid',
     QTY_TEXT varchar2(60)path '$.domain.interwarehouse_onward_source.quantity',
     UOM_TEXT varchar2(20)path '$.domain.interwarehouse_onward_source.base_uom'))loaded
     on loaded.GROUP_PLAN=gp.OPERATION_ID and loaded.LOT_UID=expected.SOURCE_UID and loaded.QTY_TEXT=expected.SOURCE_QTY and loaded.UOM_TEXT=expected.SOURCE_UOM
    where lf.TT_ID=p_trip and lf.STATUS='LOADED'and o.COMMAND_TYPE='HU_SHIP');
   j:=json_object_t();j.put('plan_operation_id',gp.OPERATION_ID);j.put('grouped_cargo',true);j.put('physically_loaded',n=0);a.append(j);
  end loop;
  return a.to_clob;  
 end;  
 procedure assert_ready(p_promises clob)is a json_array_t:=json_array_t.parse(p_promises);j json_object_t;  
 begin  
  for i in 0..a.get_size-1 loop j:=treat(a.get(i)as json_object_t);if not j.get_boolean('physically_loaded')then raise_application_error(-20886,'DEPART_EXPECTED_INTERWARE_CARGO_NOT_READY: '||j.get_string('plan_operation_id'));end if;end loop;  
 end;  
end;
/
