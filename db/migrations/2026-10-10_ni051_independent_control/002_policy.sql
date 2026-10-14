create or replace package RRL_STOCK_QC_POLICY authid definer as
 procedure settings(p_warehouse number,p_mode out varchar2,p_independent out number);
 function controller_allowed(p_domain clob,p_actor varchar2) return number;
 procedure assert_controller(p_domain clob,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_QC_POLICY as
 procedure settings(p_warehouse number,p_mode out varchar2,p_independent out number) is
 begin
  select nvl(s.OUTGOING_QC_MODE,case when nvl(w.BLOCK_IF_NO_PROOVE,0)=1 then 'ANY' else 'NONE' end),
   nvl(s.OUTGOING_QC_INDEPENDENT,0) into p_mode,p_independent from RRL_WARES w
   left join RRL_RECEIPT_WARE_SETTINGS s on s.WARE_ID=w.ID where w.ID=p_warehouse;
 end;
 function controller_allowed(p_domain clob,p_actor varchar2) return number is
  d json_object_t:=json_object_t.parse(p_domain);v_mode varchar2(10);v_independent number;
  v_case number:=d.get_number('case_task');v_id number:=d.get_number('document_id');v_known number:=0;v_count number;v_actor varchar2(100);
 begin
  settings(d.get_number('warehouse'),v_mode,v_independent);if v_independent=0 then return 1;end if;
  if p_actor is null then return 0;end if;
  if v_case is not null then
   for z in(select h.CREATED_BY,op.ACTOR,op.STATE from RRL_CASE_CARRIER_LOT h left join RRL_STOCK_OPERATION op on op.OPERATION_ID=h.CREATED_OPERATION
    where h.CASE_PICK_TASK_ID=v_case order by h.LOT_UID fetch first 201 rows only) loop
    v_known:=v_known+1;
    if v_known>200 or z.ACTOR is null or z.CREATED_BY is null or z.STATE!='APPLIED' or z.CREATED_BY!=z.ACTOR then return 0;end if;
    if z.ACTOR=p_actor then return 0;end if;
   end loop;
  else
   for z in(select m.CREATED_BY,op.ACTOR,op.STATE from RRL_CUSTOMER_ORDER_FULFILLMENT ff
    join RRL_WAREHOUSE_TASK_STOCK_MOVE m on m.TASK_ID=ff.PICKED_WAREHOUSE_TASK_ID
    left join RRL_STOCK_OPERATION op on op.OPERATION_ID=m.OPERATION_ID
    where ff.LEGACY_SBORKA_PALLET_ID=v_id order by m.OPERATION_ID fetch first 201 rows only) loop
    v_known:=v_known+1;
    if v_known>200 or z.ACTOR is null or z.CREATED_BY is null or z.STATE!='APPLIED' or z.CREATED_BY!=z.ACTOR then return 0;end if;
    if z.ACTOR=p_actor then return 0;end if;
   end loop;
  end if;
  if v_known=0 then return 0;end if;return 1;
 end;
 procedure assert_controller(p_domain clob,p_actor varchar2) is
 begin if controller_allowed(p_domain,p_actor)!=1 then raise_application_error(-20882,'QUALITY_INDEPENDENT_CONTROLLER_REQUIRED_ACTUAL_PICK_FACTS');end if;end;
end;
/