create or replace package RRL_IW_GROUP_PUT authid definer accessible by(package RRL_STOCK_HU_TASK)as
 procedure describe_receipt(p_receipt varchar2,p_target varchar2,p_actor varchar2,p_task number,p_domain out json_object_t);
 procedure declare_rows(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure validate_receipt(p_domain json_object_t,p_actor varchar2,p_task number);
 procedure record_plan(p_operation varchar2,p_task number,p_domain json_object_t,p_actor varchar2);
 procedure record_complete(p_operation varchar2,p_task number,p_domain json_object_t,p_actor varchar2);
end;
/
create or replace package body RRL_IW_GROUP_PUT as
 procedure describe_receipt(p_receipt varchar2,p_target varchar2,p_actor varchar2,p_task number,p_domain out json_object_t)is
 receipt RRL_IW_GROUP_RECEIPT%rowtype;tree json_object_t;nodes json_array_t;node json_object_t;line_value json_object_t;lines_value json_array_t:=json_array_t();
 n number;line_count number;wire clob;unit_count number;matched number;total number;lot_uid varchar2(200);lot_qty number;lot_uom varchar2(20);lot_article varchar2(160);
 current_p number;current_h number;stock_version number;current_uom varchar2(20);task_count number;
 begin
 select *into receipt from RRL_IW_GROUP_RECEIPT where OPERATION_ID=p_receipt;
 select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'warehouse_task_execute')=1 and(WARE_ID=receipt.WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'INTERWARE_GROUP_PLACEMENT_ACTOR_REQUIRED');end if;
 select count(*)into n from RRL_IW_GROUP_PLACEMENT where RECEIPT_OPERATION_ID=p_receipt;
 if n!=0 then raise_application_error(-20886,'INTERWARE_GROUP_ALREADY_PLACED');end if;
 select count(*)into n from RRL_IW_GROUP_PUT_PLAN p join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID where p.RECEIPT_OPERATION_ID=p_receipt and t.STATUS!='CANCELLED'and(p_task is null or p.TASK_ID!=p_task);
 if n!=0 then raise_application_error(-20886,'INTERWARE_GROUP_ACTIVE_PLACEMENT_EXISTS');end if;
 tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(receipt.ROOT_UID,p_task));nodes:=tree.get_array('nodes');
 if tree.get_string('cell')!=receipt.RECEIVE_CELL or tree.get_number('warehouse')!=receipt.WARE_ID or tree.get_array('ancestors').get_size!=0 or nodes.get_size>200 then raise_application_error(-20886,'INTERWARE_GROUP_RECEIVED_TOP_REQUIRED');end if;
 select count(*)into line_count from RRL_IW_GROUP_RECEIPT_LINE where OPERATION_ID=p_receipt;
 if tree.get_number('leaf_count')!=line_count then raise_application_error(-20886,'INTERWARE_GROUP_RECEIVED_LEAF_COUNT_CHANGED');end if;
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=p_receipt and STATE='APPLIED';
 for i in 0..nodes.get_size-1 loop
  node:=treat(nodes.get(i)as json_object_t);
  if node.get_string('kind')='STOCK'then
   lot_uid:=node.get_string('uid');lot_article:=node.get_string('article');lot_qty:=RRL_STOCK_MATH.quantity(node.get_string('quantity'));lot_uom:=node.get_string('base_uom');
   RRL_IW_GROUP_THERMAL.assert_cell(receipt.WARE_ID,lot_article,p_target);
   select count(*)into n from RRL_IW_GROUP_RECEIPT_LINE where OPERATION_ID=p_receipt and ROOT_UID=lot_uid and ARTICLE=lot_article and BASE_QTY=lot_qty and BASE_UOM=lot_uom;
   if n!=1 or node.get_number('open_task_count')>0 then raise_application_error(-20886,'INTERWARE_GROUP_EXACT_RECEIVED_LEAF_REQUIRED');end if;
   select REMAIN,HARD_RESERVED_BASE,BASE_UOM,STOCK_VERSION into current_p,current_h,current_uom,stock_version from RRL_REMAINS where UID_POLETA=lot_uid and CELL=receipt.RECEIVE_CELL;
   if current_p!=lot_qty or current_h!=0 or current_uom!=lot_uom then raise_application_error(-20886,'INTERWARE_GROUP_WHOLE_UNRESERVED_RECEIPT_REQUIRED');end if;
   select count(*)into unit_count from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=lot_uid;
   select count(*),sum(u.BASE_QTY)into matched,total from RRL_WMS_RECEIPT_UNIT u join json_table(wire,'$.domain.lots[*]'columns(U varchar2(200)path '$.uid',nested path '$.issued_manifest.units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom')))j
   on j.U=lot_uid and j.K=u.PHYSICAL_UNIT_KEY and RRL_STOCK_MATH.quantity(j.Q)=u.BASE_QTY and j.B=u.BASE_UOM
   where u.CURRENT_UID=lot_uid and u.CURRENT_CELL=receipt.RECEIVE_CELL and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null;
   if matched!=unit_count or(unit_count>0 and total!=lot_qty)then raise_application_error(-20884,'INTERWARE_GROUP_ORIGINAL_AVAILABLE_KEYS_REQUIRED');end if;
   line_value:=json_object_t();line_value.put('uid',lot_uid);line_value.put('article',lot_article);line_value.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(lot_qty));line_value.put('base_uom',lot_uom);line_value.put('stock_version',stock_version);line_value.put('physical_unit_count',unit_count);lines_value.append(line_value);
  elsif node.get_string('kind')!='CONTAINER'or node.get_number('open_task_count')>0 then raise_application_error(-20886,'INTERWARE_GROUP_SEALED_TOP_TASK_REQUIRED');end if;
 end loop;
 if p_target is null or p_target=receipt.RECEIVE_CELL then raise_application_error(-20886,'INTERWARE_GROUP_SEPARATE_PLACEMENT_REQUIRED');end if;
 p_domain:=json_object_t();p_domain.put('receipt_operation_id',p_receipt);p_domain.put('uid',receipt.ROOT_UID);p_domain.put('warehouse_id',receipt.WARE_ID);p_domain.put('from_cell',receipt.RECEIVE_CELL);p_domain.put('target_cell',p_target);p_domain.put('lines',lines_value);
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_GROUP_RECEIPT_STOCK_REQUIRED');
 end;
 procedure declare_rows(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t)is
 begin
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_IW_GROUP_RECEIPT',p_domain.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_IW_GROUP_PUT_PLAN',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_IW_GROUP_PLACEMENT',p_operation);
 end;
 procedure validate_receipt(p_domain json_object_t,p_actor varchar2,p_task number)is
 fresh json_object_t;left_wire clob;right_wire clob;n number;
 begin
 describe_receipt(p_domain.get_string('receipt_operation_id'),p_domain.get_string('target_cell'),p_actor,p_task,fresh);
 left_wire:=fresh.to_clob;right_wire:=p_domain.to_clob;select count(*)into n from dual where json_equal(left_wire,right_wire);
 if n!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: grouped received HU');end if;
 end;
 procedure record_plan(p_operation varchar2,p_task number,p_domain json_object_t,p_actor varchar2)is
 v_receipt varchar2(100):=p_domain.get_string('receipt_operation_id');v_uid varchar2(200):=p_domain.get_string('uid');v_ware number:=p_domain.get_number('warehouse_id');v_from varchar2(60):=p_domain.get_string('from_cell');v_target varchar2(60):=p_domain.get_string('target_cell');
 begin
 insert into RRL_IW_GROUP_PUT_PLAN(OPERATION_ID,RECEIPT_OPERATION_ID,TASK_ID,ROOT_UID,WARE_ID,FROM_CELL,TARGET_CELL,ACTOR)values(p_operation,v_receipt,p_task,v_uid,v_ware,v_from,v_target,p_actor);
 end;
 procedure record_complete(p_operation varchar2,p_task number,p_domain json_object_t,p_actor varchar2)is
 v_receipt varchar2(100):=p_domain.get_string('receipt_operation_id');v_uid varchar2(200):=p_domain.get_string('uid');v_ware number:=p_domain.get_number('warehouse_id');v_target varchar2(60):=p_domain.get_string('target_cell');
 begin
 insert into RRL_IW_GROUP_PLACEMENT(OPERATION_ID,RECEIPT_OPERATION_ID,TASK_ID,ROOT_UID,WARE_ID,TARGET_CELL,ACTOR)values(p_operation,v_receipt,p_task,v_uid,v_ware,v_target,p_actor);
 end;
end;
/
