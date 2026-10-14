create or replace package RRL_IW_GROUP_CUSTODY_CORE authid definer accessible by(package RRL_STOCK_INTERWARE_CUSTODY)as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_IW_GROUP_CUSTODY_CORE as
 procedure describe_source(p_receipt varchar2,p_actor varchar2,p_domain out json_object_t)is
 receipt RRL_IW_GROUP_RECEIPT%rowtype;plan RRL_IW_GROUP_PLAN%rowtype;placed RRL_IW_GROUP_PLACEMENT%rowtype;cargo RRL_TT_HU_LOAD_FACT%rowtype;
 unloaded RRL_IW_GROUP_UNLOAD%rowtype;n number;expected number;lines_value json_array_t:=json_array_t();x json_object_t;tree json_object_t;
 begin
 select *into receipt from RRL_IW_GROUP_RECEIPT where OPERATION_ID=p_receipt;
 select *into plan from RRL_IW_GROUP_PLAN where OPERATION_ID=receipt.PLAN_OPERATION_ID;
 select *into placed from RRL_IW_GROUP_PLACEMENT where RECEIPT_OPERATION_ID=p_receipt;
 select *into unloaded from RRL_IW_GROUP_UNLOAD where OPERATION_ID=receipt.UNLOAD_OPERATION_ID;
 select *into cargo from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=plan.SOURCE_LOAD_OPERATION_ID;
 select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'interwarehouse_receive')=1 and(WARE_ID=receipt.WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'INTERWARE_GROUP_CUSTODY_RECEIVER_REQUIRED');end if;
 if cargo.STATUS!='DEPARTED'or cargo.CUSTODY_RELEASED_AT is not null or cargo.CUSTODY_RELEASE_OPERATION_ID is not null or cargo.ROOT_UID!=receipt.ROOT_UID or unloaded.ROOT_UID!=receipt.ROOT_UID or unloaded.PLAN_OPERATION_ID!=receipt.PLAN_OPERATION_ID then raise_application_error(-20886,'INTERWARE_GROUP_CUSTODY_ORIGINAL_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_IW_GROUP_CUSTODY where RECEIPT_OPERATION_ID=p_receipt;if n!=0 then raise_application_error(-20886,'INTERWARE_GROUP_CUSTODY_ALREADY_RELEASED');end if;
 tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(receipt.ROOT_UID));
 select count(*)into expected from RRL_IW_GROUP_RECEIPT_LINE where OPERATION_ID=p_receipt;
 if tree.get_number('leaf_count')!=expected or tree.get_number('warehouse')!=receipt.WARE_ID or tree.get_string('cell')!=placed.TARGET_CELL or tree.get_array('ancestors').get_size!=0 then raise_application_error(-20886,'INTERWARE_GROUP_CUSTODY_PLACED_TOP_REQUIRED');end if;
 declare tree_wire clob:=tree.to_clob;begin
 select count(*)into n from RRL_IW_GROUP_RECEIPT_LINE l join json_table(tree_wire,'$.nodes[*]'columns(K varchar2(20)path '$.kind',U varchar2(200)path '$.uid',A varchar2(160)path '$.article',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))j on j.K='STOCK'and j.U=l.ROOT_UID and j.A=l.ARTICLE and RRL_STOCK_MATH.quantity(j.Q)=l.BASE_QTY and j.B=l.BASE_UOM where l.OPERATION_ID=p_receipt;
 if n!=expected then raise_application_error(-20886,'INTERWARE_GROUP_CUSTODY_EXACT_TREE_LEAVES_REQUIRED');end if;end;
 for line_value in(select l.ROOT_UID,l.ARTICLE,l.BASE_QTY,l.BASE_UOM,r.REMAIN,r.HARD_RESERVED_BASE,r.STOCK_VERSION,r.BASE_UOM STOCK_UOM
  from RRL_IW_GROUP_RECEIPT_LINE l left join RRL_REMAINS r on r.UID_POLETA=l.ROOT_UID and r.CELL=placed.TARGET_CELL
  where l.OPERATION_ID=p_receipt order by l.ROOT_UID)loop
  if line_value.REMAIN is null or line_value.REMAIN!=line_value.BASE_QTY or line_value.HARD_RESERVED_BASE!=0 or line_value.STOCK_UOM!=line_value.BASE_UOM then raise_application_error(-20886,'INTERWARE_GROUP_CUSTODY_EXACT_FREE_STOCK_REQUIRED');end if;
  x:=json_object_t();x.put('uid',line_value.ROOT_UID);x.put('article',line_value.ARTICLE);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(line_value.BASE_QTY));x.put('base_uom',line_value.BASE_UOM);x.put('stock_version',line_value.STOCK_VERSION);lines_value.append(x);
 end loop;
 p_domain:=json_object_t();p_domain.put('group_custody',true);p_domain.put('receipt_operation_id',p_receipt);p_domain.put('unload_operation_id',receipt.UNLOAD_OPERATION_ID);p_domain.put('source_load_operation_id',plan.SOURCE_LOAD_OPERATION_ID);p_domain.put('uid',receipt.ROOT_UID);p_domain.put('warehouse_id',receipt.WARE_ID);p_domain.put('cell',placed.TARGET_CELL);p_domain.put('lines',lines_value);
 p_domain.put('custody_released_at',to_char(unloaded.CREATED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));p_domain.put('departure_operation_id',cargo.DEPARTURE_OPERATION_ID);
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_GROUP_CUSTODY_PLACEMENT_REQUIRED');
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();lines_value json_array_t;x json_object_t;
 begin
 describe_source(d.get_object('source').get_string('receipt_operation_id'),d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_IW_GROUP_RECEIPT',v.get_string('receipt_operation_id'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_IW_GROUP_UNLOAD',v.get_string('unload_operation_id'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_IW_GROUP_CUSTODY',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',v.get_string('source_load_operation_id'));RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v.get_string('uid'));RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TT.LOAD.HU:'||v.get_string('uid'));
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 lines_value:=v.get_array('lines');for i in 0..lines_value.get_size-1 loop x:=treat(lines_value.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),v.get_string('cell'),null);end loop;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');wire clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 receipt_id varchar2(100);load_id varchar2(100);unload_id varchar2(100);release_time timestamp with time zone;left_wire clob;right_wire clob;n number;
 begin
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(wire).get_object('domain');
 receipt_id:=v.get_string('receipt_operation_id');load_id:=v.get_string('source_load_operation_id');unload_id:=v.get_string('unload_operation_id');
 describe_source(receipt_id,p_actor,fresh);left_wire:=fresh.to_clob;right_wire:=v.to_clob;select count(*)into n from dual where json_equal(left_wire,right_wire);
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_CUSTODY_SOURCE_CHANGED');end if;
 select CREATED_AT into release_time from RRL_IW_GROUP_UNLOAD where OPERATION_ID=unload_id;
 insert into RRL_IW_GROUP_CUSTODY(OPERATION_ID,RECEIPT_OPERATION_ID,SOURCE_LOAD_OPERATION_ID,ACTOR)values(op,receipt_id,load_id,p_actor);
 update RRL_TT_HU_LOAD_FACT set CUSTODY_RELEASED_AT=release_time,CUSTODY_RELEASE_OPERATION_ID=op where LOAD_OPERATION_ID=load_id and CUSTODY_RELEASED_AT is null and CUSTODY_RELEASE_OPERATION_ID is null;
 if sql%rowcount!=1 then raise_application_error(-20886,'INTERWARE_GROUP_CUSTODY_COMPARE_SET_CONFLICT');end if;
 j.put('operation_id',op);j.put('receipt_operation_id',receipt_id);j.put('source_load_operation_id',load_id);j.put('pallet_identifier',v.get_string('uid'));j.put('warehouse_id',v.get_number('warehouse_id'));j.put('status','FIRST_LEG_CUSTODY_RELEASED');j.put('custody_released_at',v.get_string('custody_released_at'));j.put('stock_changed',false);j.put('customer_delivery_confirmed',false);p_result:=j.to_clob;
 end;
end;
/
