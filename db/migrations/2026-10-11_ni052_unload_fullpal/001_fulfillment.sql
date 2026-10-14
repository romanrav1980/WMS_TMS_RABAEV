create or replace package RRL_STOCK_FULFILLMENT_FACT authid definer
 accessible by(package RRL_STOCK_UNLOAD_CMD,package RRL_STOCK_SHIPPING_CORE) as
 procedure project_ship(p_shipment number,p_identifier varchar2,p_order number,p_operation varchar2,p_facts clob,p_actor varchar2);
 procedure project_unload(p_shipment number,p_load varchar2,p_case number,p_actor varchar2);
 procedure project_unload_pallet(p_shipment number,p_load varchar2,p_uid varchar2,p_actor varchar2);
end;
/

create or replace package body RRL_STOCK_FULFILLMENT_FACT as
 procedure project_ship(p_shipment number,p_identifier varchar2,p_order number,p_operation varchar2,p_facts clob,p_actor varchar2) is
  a json_array_t:=json_array_t();x json_object_t;v_total number:=0;v_unit varchar2(20);v_mixed number:=0;v_count number:=0;v_comp clob;
 begin
  for f in(select ARTICLE,BASE_UOM,sum(QTY) QTY from json_table(p_facts,'$[*]' columns(
   ARTICLE varchar2(160) path '$.article' error on error,
   BASE_UOM varchar2(20) path '$.base_uom' error on error,
   QTY number path '$.quantity' error on error)) group by ARTICLE,BASE_UOM order by ARTICLE,BASE_UOM) loop
   if f.ARTICLE is null or f.BASE_UOM is null or f.QTY<=0 then raise_application_error(-20887,'SHIPPED_FACT_COMPOSITION_INVALID');end if;
   if a.get_size>=200 then raise_application_error(-20881,'SHIPPED_FACT_COMPOSITION_BOUND');end if;
   x:=json_object_t();x.put('article',f.ARTICLE);x.put('base_uom',f.BASE_UOM);
   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(f.QTY));a.append(x);
   if v_unit is null then v_unit:=f.BASE_UOM;elsif v_unit!=f.BASE_UOM then v_mixed:=1;end if;
   v_total:=v_total+f.QTY;
  end loop;
  if a.get_size=0 then raise_application_error(-20887,'SHIPPED_FACT_COMPOSITION_EMPTY');end if;
  v_comp:=a.to_clob;
  for ff in(select FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=p_shipment
   and PALLET_UID=p_identifier and CUSTOMER_ORDER_ID=p_order order by FULFILLMENT_ID for update) loop
   v_count:=v_count+1;if v_count>1 then raise_application_error(-20887,'SHIPMENT_FULFILLMENT_AMBIGUOUS');end if;
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff.FULFILLMENT_ID)));
   update RRL_CUSTOMER_ORDER_FULFILLMENT set STATUS='SHIPPED',
    FACT_QTY=case when v_mixed=0 then v_total else null end,FACT_UOM=case when v_mixed=0 then v_unit else null end,
    FACT_COMPOSITION_JSON=v_comp,SHIPPED_OPERATION_ID=p_operation,SHIPPED_AT=systimestamp,
    UPDATED_AT=sysdate,UPDATED_BY=p_actor where FULFILLMENT_ID=ff.FULFILLMENT_ID;
  end loop;
  if v_count!=1 then raise_application_error(-20887,'SHIPMENT_FULFILLMENT_MISSING');end if;
 end;
 procedure project_unload(p_shipment number,p_load varchar2,p_case number,p_actor varchar2)is n number:=0;version_no number;
 begin
  select CONTENT_VERSION into version_no from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_case;
  for ff in(select FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=p_shipment and PICKED_CASE_TASK_ID=p_case and STATUS='SHIPPED'and SHIPPED_OPERATION_ID=p_load order by FULFILLMENT_ID for update)loop
   n:=n+1;
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff.FULFILLMENT_ID)));
   update RRL_CUSTOMER_ORDER_FULFILLMENT set STATUS='PICKED',SHIPPED_OPERATION_ID=null,SHIPPED_AT=null,PICKED_CONTENT_VERSION=version_no,UPDATED_AT=sysdate,UPDATED_BY=p_actor where FULFILLMENT_ID=ff.FULFILLMENT_ID;
  end loop;
  if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULFILLMENT_REQUIRED');end if;
 end;
 procedure project_unload_pallet(p_shipment number,p_load varchar2,p_uid varchar2,p_actor varchar2)is n number:=0;version_no number;
 begin
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));
  select STOCK_VERSION into version_no from RRL_REMAINS where UID_POLETA=p_uid and REMAIN>0 and HARD_RESERVED_BASE=REMAIN;
  for ff in(select FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=p_shipment and PICKED_CASE_TASK_ID is null and PICKED_PALLET_UID=p_uid and PICKED_WAREHOUSE_TASK_ID is not null and STATUS='SHIPPED'and SHIPPED_OPERATION_ID=p_load order by FULFILLMENT_ID for update)loop
   n:=n+1;RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff.FULFILLMENT_ID)));
   update RRL_CUSTOMER_ORDER_FULFILLMENT set STATUS='PICKED',SHIPPED_OPERATION_ID=null,SHIPPED_AT=null,PICKED_STOCK_VERSION=version_no,UPDATED_AT=sysdate,UPDATED_BY=p_actor where FULFILLMENT_ID=ff.FULFILLMENT_ID;
  end loop;
  if n!=1 then raise_application_error(-20886,'UNLOAD_ORIGINAL_FULLPAL_FULFILLMENT_REQUIRED');end if;
 end;
end;
/
