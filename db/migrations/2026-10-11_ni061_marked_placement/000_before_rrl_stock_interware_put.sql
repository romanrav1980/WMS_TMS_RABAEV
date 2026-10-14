create or replace package RRL_STOCK_INTERWARE_PUT authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t);
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2);
end;
/

create or replace package body RRL_STOCK_INTERWARE_PUT as
 procedure describe_current(p_receipt varchar2,p_actor varchar2,p_task number,p_domain out json_object_t) is
 receipt RRL_INTERWARE_RECEIPT%rowtype;plan RRL_INTERWARE_PLAN%rowtype;
 v_target varchar2(60);v_p number;v_h number;v_unit varchar2(20);v_ver number;v_capacity number;v_height number;v_weight number;v_unknown number;v_gross number;n number;
 begin
 select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=p_receipt;
 select *into plan from RRL_INTERWARE_PLAN where OPERATION_ID=receipt.PLAN_OPERATION_ID;
 select count(*)into n from RUSERS u where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=receipt.WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1;
 if n!=1 then raise_application_error(-20882,'INTERWARE_PLACEMENT_ACTOR_REQUIRED');end if;
 v_target:=plan.OUTBOUND_DOCK;
 select count(*)into n from RRL_TRANSPORT_TASK t join RRL_TT_DOCK d on d.DOCK=t.DOCK where t.ID=plan.TARGET_TT_ID and t.DOCK=v_target and d.WARE_ID=receipt.WARE_ID and nvl(d.DOCK_IS_BLOCKED,0)=0 and t.CONDITION='Спланирован'and nvl(t.DELETED,0)=0;
 if n!=1 then raise_application_error(-20886,'INTERWARE_ORIGINAL_TARGET_TRIP_UNAVAILABLE');end if;
 select LIMIT_WEIGHT,LIMIT_HEIGHT into v_capacity,v_height from RRL_CELLS where CELL=v_target and WARE_ID=receipt.WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0 and nvl(BLOCKED_FOR_REMAINS,0)=0 and nvl(BLOCKED_FOR_POPOLNENIE,0)=0;
 if v_target=receipt.RECEIVE_CELL then raise_application_error(-20886,'INTERWARE_SEPARATE_OUTBOUND_BUFFER_REQUIRED');end if;
 if nvl(v_height,0)>0 then raise_application_error(-20886,'INTERWARE_TARGET_HEIGHT_PROOF_REQUIRED');end if;
 select count(*)into n from RRL_TOPOLOGY_CELL_SLOT sl join RRL_TOPOLOGY_CELL tc on tc.TOPOLOGY_CELL_ID=sl.TOPOLOGY_CELL_ID join RRL_WAREHOUSE_TOPOLOGY t on t.TOPOLOGY_ID=tc.TOPOLOGY_ID where tc.LEGACY_CELL_CODE=v_target and tc.WARE_ID=receipt.WARE_ID and tc.ACTIVE=1 and sl.ACTIVE=1 and t.STATUS='PUBLISHED';
 if n!=0 then raise_application_error(-20886,'INTERWARE_TARGET_SLOT_FLOW_REQUIRED');end if;
 select count(*)into n from RRL_INTERWARE_PLACEMENT where RECEIPT_OPERATION_ID=p_receipt;if n!=0 then raise_application_error(-20886,'INTERWARE_ALREADY_PLACED');end if;
 select count(*)into n from RRL_INTERWARE_PUT_PLAN p join RRL_WAREHOUSE_TASK wt on wt.TASK_ID=p.TASK_ID where p.RECEIPT_OPERATION_ID=p_receipt and wt.STATUS!='CANCELLED'and(p_task is null or wt.TASK_ID!=p_task);
 if n!=0 then raise_application_error(-20886,'INTERWARE_ACTIVE_PLACEMENT_EXISTS');end if;
 select REMAIN,HARD_RESERVED_BASE,BASE_UOM,STOCK_VERSION into v_p,v_h,v_unit,v_ver from RRL_REMAINS where UID_POLETA=receipt.ROOT_UID and CELL=receipt.RECEIVE_CELL;
 if v_p!=receipt.BASE_QTY or v_h!=0 or v_unit!=receipt.BASE_UOM then raise_application_error(-20886,'INTERWARE_WHOLE_UNRESERVED_RECEIPT_REQUIRED');end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA=receipt.ROOT_UID and CELL!=receipt.RECEIVE_CELL and(REMAIN!=0 or HARD_RESERVED_BASE!=0);if n!=0 then raise_application_error(-20886,'INTERWARE_MULTIPLE_STOCK_CELLS_DENIED');end if;
 select count(*)into n from dual where exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=receipt.ARTICLE)or exists(select 1 from RRL_SKU_RECEIPT_POLICY where ARTICUL=receipt.ARTICLE and MARKING_REQUIRED=1)or exists(select 1 from RRL_FINISHED_GOODS_SKU where ARTICUL=receipt.ARTICLE and CRPT_REQUIRED=1);
 if n!=0 then raise_application_error(-20886,'INTERWARE_MARKED_PLACEMENT_FLOW_REQUIRED');end if;
 select GROSS_WEIGHT_KG into v_gross from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=receipt.SOURCE_LOAD_OPERATION_ID;
 if nvl(v_capacity,0)>0 then
  select nvl(sum(pp.WEIGHT_BRUTTO),0),nvl(sum(case when pp.WEIGHT_BRUTTO is null then 1 else 0 end),0)into v_weight,v_unknown from(
   select r.UID_POLETA UID_PALLET from RRL_REMAINS r where r.CELL=v_target and r.REMAIN>0 and r.UID_POLETA!=receipt.ROOT_UID
   union select wt.UID_PALLET from RRL_WAREHOUSE_TASK wt where wt.TO_CELL=v_target and wt.STATUS not in('DONE','CANCELLED')and wt.UID_PALLET!=receipt.ROOT_UID and(p_task is null or wt.TASK_ID!=p_task)
  )occupants join RRL_PALLETS pp on pp.UID_PALLET=occupants.UID_PALLET;
  if v_gross is null or v_unknown>0 or v_weight+v_gross>v_capacity then raise_application_error(-20886,'INTERWARE_TARGET_WEIGHT_CAPACITY_EXCEEDED');end if;
 end if;
 p_domain:=json_object_t();p_domain.put('receipt_operation_id',p_receipt);p_domain.put('plan_operation_id',receipt.PLAN_OPERATION_ID);p_domain.put('warehouse_id',receipt.WARE_ID);p_domain.put('uid',receipt.ROOT_UID);p_domain.put('article',receipt.ARTICLE);
 p_domain.put('from_cell',receipt.RECEIVE_CELL);p_domain.put('target_cell',v_target);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(receipt.BASE_QTY));p_domain.put('base_uom',receipt.BASE_UOM);p_domain.put('stock_version',v_ver);p_domain.put('target_trip_id',plan.TARGET_TT_ID);
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_RECEIPT_OUTBOUND_CELL_REQUIRED');
 end;
 procedure declare_rows(p_domain json_object_t,p_resources in out nocopy json_array_t) is
 begin
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_RECEIPT',p_domain.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_PLAN',p_domain.get_string('plan_operation_id'));
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();v_task number;
 begin
 describe_current(d.get_object('source').get_string('receipt_operation_id'),d.get_string('actor'),null,v);
 select RRL_WAREHOUSE_TASK_SQ.nextval into v_task from dual;v.put('task_id',v_task);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 declare_rows(v,r);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_PUT_PLAN',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task));
 RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('uid'),v.get_string('article'),v.get_string('from_cell'),v.get_string('target_cell'));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');resolved clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_receipt varchar2(100);v_task number;v_ware number;v_uid varchar2(200);v_article varchar2(160);v_from varchar2(60);v_to varchar2(60);v_unit varchar2(20);v_qty number;
 begin
 select RESOLVED_PLAN_JSON into resolved from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(resolved).get_object('domain');v_receipt:=v.get_string('receipt_operation_id');v_task:=v.get_number('task_id');
 describe_current(v_receipt,p_actor,null,fresh);fresh.put('task_id',v_task);
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'INTERWARE_PLACEMENT_PLAN_CHANGED');end if;
 v_ware:=v.get_number('warehouse_id');v_uid:=v.get_string('uid');v_article:=v.get_string('article');v_from:=v.get_string('from_cell');v_to:=v.get_string('target_cell');v_unit:=v.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));
 insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,TARGET_ARTICUL,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY)
 values(v_task,'PUTAWAY','MANUAL',v_task,'INTERWARE',v_task,v_uid,v_article,v_from,v_to,v_ware,v_ware,v_qty,v_unit,'PALLET','PLANNED',p_actor);
 insert into RRL_INTERWARE_PUT_PLAN(OPERATION_ID,RECEIPT_OPERATION_ID,TASK_ID,TARGET_CELL,ACTOR)values(op,v_receipt,v_task,v_to,p_actor);
 j.put('operation_id',op);j.put('task_id',v_task);j.put('receipt_operation_id',v_receipt);j.put('from_cell',v_from);j.put('to_cell',v_to);j.put('quantity',v.get_string('quantity'));j.put('base_uom',v_unit);j.put('stock_changed',false);p_result:=j.to_clob;
 end;
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t) is
 v_receipt varchar2(100);v_target varchar2(60);v json_object_t;
 begin
 select RECEIPT_OPERATION_ID,TARGET_CELL into v_receipt,v_target from RRL_INTERWARE_PUT_PLAN where TASK_ID=p_task.TASK_ID;
 describe_current(v_receipt,p_actor,p_task.TASK_ID,v);
 if p_task.TASK_SOURCE!='MANUAL' or p_task.TASK_TYPE!='PUTAWAY' or p_task.SOURCE_DOC_TYPE!='INTERWARE' or p_task.SOURCE_DOC_ID!=p_task.TASK_ID or p_task.UID_PALLET!=v.get_string('uid') or p_task.FROM_CELL!=v.get_string('from_cell') or p_task.TO_CELL!=v.get_string('target_cell') or p_task.UNIT_CODE!=v.get_string('base_uom') or p_task.QTY!=RRL_STOCK_MATH.quantity(v.get_string('quantity')) or p_task.QTY_MODE!='PALLET' or v_target!=p_task.TO_CELL then raise_application_error(-20886,'INTERWARE_ORIGINAL_TASK_REQUIRED');end if;
 declare_rows(v,p_resources);RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_PLACEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(p_task.TASK_ID));
 p_domain.put('interwarehouse_placement',v);
 end;
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t) is
 resources json_array_t:=json_array_t();domain json_object_t:=json_object_t();
 begin
 plan_task(p_task,p_actor,resources,domain);
 if dbms_lob.compare(p_frozen.to_clob,domain.get_object('interwarehouse_placement').to_clob)!=0 then raise_application_error(-20886,'INTERWARE_TASK_SOURCE_CHANGED');end if;
 end;
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2) is
 v_receipt varchar2(100);receipt RRL_INTERWARE_RECEIPT%rowtype;op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_json clob;
 begin
 select RECEIPT_OPERATION_ID into v_receipt from RRL_INTERWARE_PUT_PLAN where TASK_ID=p_task.TASK_ID;select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=v_receipt;
 if p_quantity!=receipt.BASE_QTY or p_target_uid!=receipt.ROOT_UID then raise_application_error(-20886,'INTERWARE_WHOLE_PLACEMENT_REQUIRED');end if;
 insert into RRL_INTERWARE_PLACEMENT(TASK_ID,RECEIPT_OPERATION_ID,OPERATION_ID,ROOT_UID,WARE_ID,TARGET_CELL,BASE_QTY,BASE_UOM,ACTOR)values(p_task.TASK_ID,v_receipt,op,receipt.ROOT_UID,receipt.WARE_ID,p_task.TO_CELL,receipt.BASE_QTY,receipt.BASE_UOM,p_actor);
 end;
end;
/
