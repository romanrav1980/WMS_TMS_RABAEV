from pathlib import Path
import json
d='db/migrations/2026-10-12_ni061_group_onward';out={}
out[d+'/001_schema.sql']="""begin execute immediate q'[create table RRL_IW_GROUP_ONWARD(
 OPERATION_ID varchar2(100)primary key,PAYLOAD_HASH raw(32)not null,
 RECEIPT_OPERATION_ID varchar2(100)not null unique references RRL_IW_GROUP_RECEIPT(OPERATION_ID),
 ACTOR nvarchar2(50)not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_IW_GROUP_ST_BIND(
 OPERATION_ID varchar2(100)primary key,ONWARD_OPERATION_ID varchar2(100)not null references RRL_IW_GROUP_ONWARD(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null references RRL_IW_GROUP_RECEIPT(OPERATION_ID),
 ST_ID number not null unique references RRL_SBORKA_PALLETS(ID),ST_IDENTIFIER varchar2(50)not null unique,
 SOURCE_ST_ID number not null,SOURCE_LOAD_OPERATION_ID varchar2(100)not null,TARGET_TT_ID number not null,
 WARE_ID number not null,ROOT_UID varchar2(200)not null,STOCK_VERSION number not null,SOURCE_CELL varchar2(60)not null,
 FINAL_ADDRESS varchar2(4000)not null,ORIGINAL_FULFILLMENT_JSON clob not null check(ORIGINAL_FULFILLMENT_JSON is json),
 ACTOR nvarchar2(50)not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 constraint RRL_IW_GROUP_BIND_LOT_UQ unique(RECEIPT_OPERATION_ID,ROOT_UID)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_IW_GROUP_DISPATCH(
 OPERATION_ID varchar2(100)not null references RRL_STOCK_OPERATION(OPERATION_ID),
 BIND_OPERATION_ID varchar2(100)not null unique references RRL_IW_GROUP_ST_BIND(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null,SOURCE_LOAD_OPERATION_ID varchar2(100)not null,
 ST_ID number not null,ROOT_UID varchar2(200)not null,BASE_QTY number not null check(BASE_QTY>0),
 BASE_UOM varchar2(20)not null,ACTOR nvarchar2(50)not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_IW_GROUP_DISPATCH_PK primary key(OPERATION_ID,ST_ID)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_IW_GROUP_DISPATCH_SRC_IX on RRL_IW_GROUP_DISPATCH(SOURCE_LOAD_OPERATION_ID,ROOT_UID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
"""
out[d+'/002_next.sql']="""create or replace package RRL_IW_GROUP_NEXT authid definer accessible by(package RRL_STOCK_INTERWARE_NEXT)as
 function describe_source(p_st number,p_ware number)return json_object_t;
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure validate_load(p_source json_object_t,p_actor varchar2);
 procedure dispatched(p_source json_object_t,p_actor varchar2);
end;
/
create or replace package body RRL_IW_GROUP_NEXT as
 function describe_source(p_st number,p_ware number)return json_object_t is
 bind RRL_IW_GROUP_ST_BIND%rowtype;receipt RRL_IW_GROUP_RECEIPT_LINE%rowtype;parent RRL_IW_GROUP_RECEIPT%rowtype;plan RRL_IW_GROUP_PLAN%rowtype;placed RRL_IW_GROUP_PLACEMENT%rowtype;
 v_p number;v_h number;v_uom varchar2(20);v_ver number;v_policy number;n number;unit_count number;unit_total number;unit_wire clob;unit_snapshot clob;wire clob;j json_object_t:=json_object_t();
 begin
 begin select *into bind from RRL_IW_GROUP_ST_BIND where ST_ID=p_st;exception when no_data_found then return null;end;
 select *into parent from RRL_IW_GROUP_RECEIPT where OPERATION_ID=bind.RECEIPT_OPERATION_ID;
 select *into receipt from RRL_IW_GROUP_RECEIPT_LINE where OPERATION_ID=parent.OPERATION_ID and ROOT_UID=bind.ROOT_UID;
 select *into plan from RRL_IW_GROUP_PLAN where OPERATION_ID=parent.PLAN_OPERATION_ID;
 select *into placed from RRL_IW_GROUP_PLACEMENT where RECEIPT_OPERATION_ID=parent.OPERATION_ID;
 if p_ware!=parent.WARE_ID or bind.WARE_ID!=p_ware or placed.TARGET_CELL!=bind.SOURCE_CELL or bind.SOURCE_ST_ID!=receipt.ST_ID or bind.SOURCE_LOAD_OPERATION_ID!=plan.SOURCE_LOAD_OPERATION_ID or bind.TARGET_TT_ID!=plan.TARGET_TT_ID then raise_application_error(-20886,'INTERWARE_GROUP_ORIGINAL_LINEAGE_REQUIRED');end if;
 select count(*)into n from RRL_IW_GROUP_CUSTODY where RECEIPT_OPERATION_ID=parent.OPERATION_ID;
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_FIRST_CUSTODY_REQUIRED');end if;
 select count(*)into n from RRL_IW_GROUP_DISPATCH where BIND_OPERATION_ID=bind.OPERATION_ID;
 if n!=0 then raise_application_error(-20886,'INTERWARE_GROUP_ALREADY_DISPATCHED');end if;
 select REMAIN,HARD_RESERVED_BASE,BASE_UOM,STOCK_VERSION into v_p,v_h,v_uom,v_ver from RRL_REMAINS where UID_POLETA=bind.ROOT_UID and CELL=bind.SOURCE_CELL;
 if v_p!=receipt.BASE_QTY or v_h!=0 or v_uom!=receipt.BASE_UOM or v_ver!=bind.STOCK_VERSION then raise_application_error(-20886,'INTERWARE_GROUP_WHOLE_FREE_STOCK_VERSION_REQUIRED');end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA=bind.ROOT_UID and CELL!=bind.SOURCE_CELL and(REMAIN!=0 or HARD_RESERVED_BASE!=0);
 if n!=0 then raise_application_error(-20886,'INTERWARE_GROUP_ONE_STOCK_CELL_REQUIRED');end if;
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=parent.OPERATION_ID and STATE='APPLIED';
 select MANIFEST into unit_wire from json_table(wire,'$.domain.lots[*]'columns(U varchar2(200)path '$.uid',MANIFEST clob format json path '$.issued_manifest'))where U=bind.ROOT_UID;
 select count(*)into unit_count from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=bind.ROOT_UID;
 if unit_count>0 then
  select count(*),sum(u.BASE_QTY),json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)
  into n,unit_total,unit_snapshot from RRL_WMS_RECEIPT_UNIT u join json_table(unit_wire,'$.units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))src on src.K=u.PHYSICAL_UNIT_KEY
  where u.CURRENT_UID=bind.ROOT_UID and u.CURRENT_CELL=bind.SOURCE_CELL and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null and u.BASE_QTY=RRL_STOCK_MATH.quantity(src.Q)and u.BASE_UOM=src.B;
  if n!=unit_count or unit_total!=receipt.BASE_QTY or json_object_t.parse(unit_wire).get_number('physical_unit_count')!=unit_count then raise_application_error(-20884,'INTERWARE_GROUP_ORIGINAL_AVAILABLE_UNITS_REQUIRED');end if;
  j.put('physical_units',json_array_t.parse(unit_snapshot));
 elsif json_object_t.parse(unit_wire).get_number('physical_unit_count')!=0 or RRL_INTERWARE_MARK_SCAN.required_for_article(receipt.ARTICLE)=1 then raise_application_error(-20884,'INTERWARE_GROUP_MARKED_SOURCE_UNITS_REQUIRED');end if;
 select max(POLICY_VERSION)into v_policy from RRL_STOCK_UOM_CONVERSION where ARTICUL=receipt.ARTICLE and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=DENOMINATOR;
 if v_policy is null then raise_application_error(-20886,'INTERWARE_GROUP_BASE_UOM_REQUIRED');end if;
 select count(*)into n from RRL_SBORKA_PALLETS where ID=p_st and WARE_ID=p_ware and ADDR=bind.FINAL_ADDRESS and RETURN_SUPPLIER_ID is null and nvl(CONDITION,0)<2 and(TRANSTASK_ID is null or TRANSTASK_ID=bind.TARGET_TT_ID);
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_ST_CHANGED');end if;
 j.put('group_receipt_operation_id',parent.OPERATION_ID);j.put('group_plan_operation_id',plan.OPERATION_ID);j.put('binding_operation_id',bind.OPERATION_ID);j.put('receipt_operation_id',parent.OPERATION_ID);j.put('source_load_operation_id',bind.SOURCE_LOAD_OPERATION_ID);j.put('source_st_id',bind.SOURCE_ST_ID);j.put('st_id',p_st);j.put('target_trip_id',bind.TARGET_TT_ID);j.put('warehouse_id',p_ware);
 j.put('uid',bind.ROOT_UID);j.put('cell',bind.SOURCE_CELL);j.put('article',receipt.ARTICLE);j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_p));j.put('base_uom',v_uom);j.put('stock_version',v_ver);j.put('uom_version',v_policy);return j;
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_GROUP_PLACED_SOURCE_REQUIRED');
 end;
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t)is
 begin
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_IW_GROUP_ST_BIND',p_source.get_string('binding_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_IW_GROUP_RECEIPT',p_source.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_IW_GROUP_DISPATCH',p_operation);
 end;
 procedure validate_load(p_source json_object_t,p_actor varchar2)is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;v_kind varchar2(80);binding_id varchar2(100):=p_source.get_string('binding_operation_id');st_id number:=p_source.get_number('st_id');trip_id number:=p_source.get_number('target_trip_id');ware_id number:=p_source.get_number('warehouse_id');fresh json_object_t;left_wire clob;right_wire clob;
 begin
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=op and STATE='IN_FLIGHT';
 if v_kind!='HU_SHIP'then raise_application_error(-20886,'INTERWARE_GROUP_WHOLE_HU_LOAD_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION o where o.OPERATION_ID=op and json_value(o.RESOLVED_PLAN_JSON,'$.domain.loading.trip'returning number)=trip_id
 and exists(select 1 from json_table(o.RESOLVED_PLAN_JSON,'$.domain.shipments[*]'columns(B varchar2(100)path '$.domain.interwarehouse_onward_source.binding_operation_id',S number path '$.domain.interwarehouse_onward_source.st_id'))s where s.B=binding_id and s.S=st_id);
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_RESOLVED_TARGET_LOAD_REQUIRED');end if;
 select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'stock_posting_shipping')=1 and(WARE_ID=ware_id or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'INTERWARE_GROUP_CURRENT_SHIPPER_REQUIRED');end if;
 fresh:=describe_source(st_id,ware_id);left_wire:=fresh.to_clob;right_wire:=p_source.to_clob;select count(*)into n from dual where json_equal(left_wire,right_wire);
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_LOAD_SOURCE_CHANGED');end if;
 select count(*)into n from RRL_SBORKA_PALLETS where ID=st_id and TRANSTASK_ID=trip_id;if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_ORIGINAL_TARGET_TRIP_REQUIRED');end if;
 end;
 procedure dispatched(p_source json_object_t,p_actor varchar2)is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');binding_id varchar2(100):=p_source.get_string('binding_operation_id');receipt_id varchar2(100):=p_source.get_string('receipt_operation_id');source_load varchar2(100):=p_source.get_string('source_load_operation_id');st_id number:=p_source.get_number('st_id');lot_id varchar2(200):=p_source.get_string('uid');qty number:=RRL_STOCK_MATH.quantity(p_source.get_string('quantity'));uom_value varchar2(20):=p_source.get_string('base_uom');payload clob;
 begin
 insert into RRL_IW_GROUP_DISPATCH(OPERATION_ID,BIND_OPERATION_ID,RECEIPT_OPERATION_ID,SOURCE_LOAD_OPERATION_ID,ST_ID,ROOT_UID,BASE_QTY,BASE_UOM,ACTOR)values(op,binding_id,receipt_id,source_load,st_id,lot_id,qty,uom_value,p_actor);
 payload:=p_source.to_clob;
 insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values('IW.GROUP:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op||':'||RRL_STOCK_PLAN_HELPER.decimal_text(st_id),'AL32UTF8'),sys.dbms_crypto.hash_sh256)),'INTERWARE_ONWARD_DISPATCHED',payload);
 end;
end;
/
"""
t=Path('tmp/native426_rrl_stock_interware_next_package_body.sql').read_text(encoding='utf-8');out[d+'/000_before_next.sql']=t
t=t.replace('return RRL_STOCK_IW_RECOVERY_NEXT.describe_source(p_st,p_ware);','declare grouped json_object_t:=RRL_IW_GROUP_NEXT.describe_source(p_st,p_ware);begin if grouped is not null then return grouped;end if;end;return RRL_STOCK_IW_RECOVERY_NEXT.describe_source(p_st,p_ware);',1)
for action in ['declare_source','validate_load','dispatched']:
 needle="if p_source.has('recovery_operation_id')then"
 insertion="if p_source.has('group_receipt_operation_id')then RRL_IW_GROUP_NEXT."+action+"("+('p_source,p_operation,p_resources'if action=='declare_source'else'p_source,p_actor')+");return;end if;\n"
 index=t.index(needle,t.index(' procedure '+action+'('));t=t[:index]+insertion+t[index:]
out[d+'/003_next_owner.sql']=t
t=Path('tmp/native426_rrl_stock_hu_ship_cmd_package_body.sql').read_text(encoding='utf-8');out[d+'/000_before_ship.sql']=t
needle="   select b.ST_ID from RRL_IW_RECOVERY_ST_BIND"
index=t.index(needle);t=t[:index]+"""   select b.ST_ID from RRL_IW_GROUP_ST_BIND b where b.WARE_ID=v_warehouse and b.SOURCE_CELL=v_source_cell and not exists(select 1 from RRL_IW_GROUP_DISPATCH dispatched where dispatched.BIND_OPERATION_ID=b.OPERATION_ID)and b.ROOT_UID in(
    select U from json_table(nodes,'$[*]'columns(U varchar2(200)path '$.uid',K varchar2(20)path '$.kind'))where K='STOCK')
   union
"""+t[index:]
out[d+'/004_ship_owner.sql']=t
print(json.dumps(out))
