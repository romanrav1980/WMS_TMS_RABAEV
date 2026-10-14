from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-10_ni062_supplier_dispatch")
out[str(f/"001_schema.sql")]=r"""begin execute immediate q'[create table RRL_STORE_RETURN_SUP_BIND(
 OPERATION_ID varchar2(100) primary key,
 PAYLOAD_HASH raw(32) not null,
 RECEIPT_OPERATION_ID varchar2(100) not null unique references RRL_STORE_RETURN_RECEIPT(OPERATION_ID),
 ST_ID number not null unique references RRL_SBORKA_PALLETS(ID),
 ST_IDENTIFIER varchar2(80 byte) not null,
 SUPPLIER_INN varchar2(255 byte) not null,
 DECISION_REFERENCE varchar2(255 byte) not null,REASON_TEXT varchar2(2000 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 RESULT_JSON clob not null check(RESULT_JSON is json)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_STORE_RETURN_SUP_DISPATCH(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 BIND_OPERATION_ID varchar2(100) not null unique references RRL_STORE_RETURN_SUP_BIND(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100) not null unique references RRL_STORE_RETURN_RECEIPT(OPERATION_ID),
 ST_ID number not null references RRL_SBORKA_PALLETS(ID),
 UID_PALLET varchar2(200 byte) not null,
 BASE_QTY number(27,9) not null check(BASE_QTY>0),BASE_UOM varchar2(20) not null,
 SUPPLIER_INN varchar2(255 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
"""
out[str(f/"002_helper.sql")]=r"""create or replace package RRL_STOCK_SUP_RETURN authid definer accessible by(package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_EFFECT_CORE) as
 function describe_source(p_st number,p_supplier varchar2,p_ware number) return json_object_t;
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure validate_consume(p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2);
 procedure dispatched(p_source json_object_t,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_SUP_RETURN as
 function describe_source(p_st number,p_supplier varchar2,p_ware number) return json_object_t is
 binding RRL_STORE_RETURN_SUP_BIND%rowtype;receipt RRL_STORE_RETURN_RECEIPT%rowtype;placed RRL_STORE_RETURN_PLACEMENT%rowtype;j json_object_t:=json_object_t();
 v_cell varchar2(60);v_qty number;v_h number;v_version number;v_uom varchar2(20);v_policy number;n number;
 begin
 begin select * into binding from RRL_STORE_RETURN_SUP_BIND where ST_ID=p_st;exception when no_data_found then return null;end;
 select * into receipt from RRL_STORE_RETURN_RECEIPT where OPERATION_ID=binding.RECEIPT_OPERATION_ID;
 select * into placed from RRL_STORE_RETURN_PLACEMENT where RECEIPT_OPERATION_ID=receipt.OPERATION_ID;
 if receipt.DISPOSITION!='SUPPLIER' or receipt.WARE_ID!=p_ware or binding.SUPPLIER_INN!=p_supplier then raise_application_error(-20886,'SUP_RETURN_TYPED_SOURCE_CONFLICT');end if;
 select count(*)into n from RRL_SUPPLIERS where INN=p_supplier;if n!=1 then raise_application_error(-20886,'SUP_RETURN_UNIQUE_SUPPLIER_REQUIRED');end if;
 select count(*)into n from RRL_STORE_RETURN_SUP_DISPATCH where BIND_OPERATION_ID=binding.OPERATION_ID;if n!=0 then raise_application_error(-20886,'SUP_RETURN_ALREADY_DISPATCHED');end if;
 select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM,CELL into v_qty,v_h,v_version,v_uom,v_cell from RRL_REMAINS where UID_POLETA=receipt.UID_PALLET and REMAIN>0;
 if v_qty!=receipt.BASE_QTY or v_h!=0 or v_uom!=receipt.BASE_UOM or v_cell!=placed.TARGET_CELL then raise_application_error(-20886,'SUP_RETURN_WHOLE_PLACED_UNRESERVED_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_CELLS where CELL=v_cell and WARE_ID=p_ware and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;
 if n!=1 then raise_application_error(-20886,'SUP_RETURN_SEGREGATED_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and(CHILD_PALLET_UID=receipt.UID_PALLET or PARENT_UID=receipt.UID_PALLET);if n!=0 then raise_application_error(-20886,'SUP_RETURN_SINGLE_PHYSICAL_PLACE_REQUIRED');end if;
 select count(*)into n from dual where exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=receipt.ARTICLE)or exists(select 1 from RRL_SKU_RECEIPT_POLICY where ARTICUL=receipt.ARTICLE and MARKING_REQUIRED=1)or exists(select 1 from RRL_FINISHED_GOODS_SKU where ARTICUL=receipt.ARTICLE and CRPT_REQUIRED=1);
 if n!=0 then raise_application_error(-20886,'SUP_RETURN_MARKED_UNIT_REGULATORY_FLOW_REQUIRED');end if;
 select max(POLICY_VERSION)into v_policy from RRL_STOCK_UOM_CONVERSION where ARTICUL=receipt.ARTICLE and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;
 if v_policy is null then raise_application_error(-20886,'SUP_RETURN_BASE_UOM_POLICY_REQUIRED');end if;
 j.put('binding_operation_id',binding.OPERATION_ID);j.put('receipt_operation_id',receipt.OPERATION_ID);j.put('st_id',p_st);j.put('supplier_inn',p_supplier);j.put('warehouse_id',p_ware);j.put('uid',receipt.UID_PALLET);j.put('cell',v_cell);j.put('article',receipt.ARTICLE);
 j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));j.put('base_uom',v_uom);j.put('stock_version',v_version);j.put('uom_version',v_policy);j.put('placement_task_id',placed.TASK_ID);j.put('return_document',receipt.SAP_OPERATION_ID);
 return j;
 exception when no_data_found then raise_application_error(-20886,'SUP_RETURN_PLACED_SOURCE_REQUIRED');when too_many_rows then raise_application_error(-20886,'SUP_RETURN_ONE_SOURCE_LOCATION_REQUIRED');end;
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t) is
 begin
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RETURN_SUP_BIND',p_source.get_string('binding_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RETURN_RECEIPT',p_source.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RETURN_SUP_DISPATCH',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(p_resources,70,'UNIQUE','SAP.OUTBOX:SUPPLIER_DISPATCH:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 end;
 procedure validate_consume(p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2) is
 v_st number;v_supplier varchar2(255);v json_object_t;op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);n number;
 begin
 if RRL_HAS_WRIGHT(p_actor,'warehouse_return_dispatch')!=1 then raise_application_error(-20882,'SUP_RETURN_DISPATCH_PERMISSION_REQUIRED');end if;
 select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=p_ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN');if n!=1 then raise_application_error(-20882,'SUP_RETURN_CURRENT_WAREHOUSE_BINDING_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=op and STATE='IN_FLIGHT';
 if v_kind!='LOAD_SHIPMENT' then raise_application_error(-20886,'SUP_RETURN_ACTUAL_PHYSICAL_LOADING_REQUIRED');end if;
 select ST_ID,SUPPLIER_INN into v_st,v_supplier from RRL_STORE_RETURN_SUP_BIND where RECEIPT_OPERATION_ID=p_receipt;
 v:=describe_source(v_st,v_supplier,p_ware);
 if v.get_string('uid')!=p_uid or v.get_string('cell')!=p_cell or RRL_STOCK_MATH.quantity(v.get_string('quantity'))!=p_quantity then raise_application_error(-20886,'SUP_RETURN_EXACT_ORIGINAL_PALLET_QUANTITY_REQUIRED');end if;
 end;
 procedure dispatched(p_source json_object_t,p_actor varchar2) is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_bind varchar2(100);v_receipt varchar2(100);v_st number;v_uid varchar2(200);v_quantity number;v_unit varchar2(20);v_supplier varchar2(255);payload json_object_t:=json_object_t();v_body clob;v_event varchar2(100);
 begin
 v_bind:=p_source.get_string('binding_operation_id');v_receipt:=p_source.get_string('receipt_operation_id');v_st:=p_source.get_number('st_id');v_uid:=p_source.get_string('uid');v_quantity:=RRL_STOCK_MATH.quantity(p_source.get_string('quantity'));v_unit:=p_source.get_string('base_uom');v_supplier:=p_source.get_string('supplier_inn');
 insert into RRL_STORE_RETURN_SUP_DISPATCH(OPERATION_ID,BIND_OPERATION_ID,RECEIPT_OPERATION_ID,ST_ID,UID_PALLET,BASE_QTY,BASE_UOM,SUPPLIER_INN,ACTOR)values(op,v_bind,v_receipt,v_st,v_uid,v_quantity,v_unit,v_supplier,p_actor);
 payload.put('operation_id',op);payload.put('receipt_operation_id',v_receipt);payload.put('supplier_inn',v_supplier);payload.put('pallet_identifier',v_uid);payload.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_quantity));payload.put('base_uom',v_unit);payload.put('warehouse_exit_confirmed',true);payload.put('supplier_received',false);payload.put('external_sap_ack',false);
 v_body:=payload.to_clob;v_event:='SUPPLIER_DISPATCH:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
 insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values(v_event,'SUPPLIER_RETURN_DISPATCHED',v_body);
 end;
end;
/
"""
s=Path("db/migrations/2026-10-08_stock_posting_core/423_before108_shipping.sql").read_text(encoding="utf-8-sig")
# Use the current deployed implementation, add only private source hooks.
s=s.replace("v_bound_uid varchar2(150);","v_supplier_source json_object_t;v_bound_uid varchar2(150);",1)
needle="  if v_customer_order is not null and v_case_task is null then"
assert needle in s
s=s.replace(needle,"""  if v_return_supplier is not null then
   v_supplier_source:=RRL_STOCK_SUP_RETURN.describe_source(v_id,v_return_supplier,v_ware);
   if v_supplier_source is not null then v_bound_uid:=v_supplier_source.get_string('uid');v_bound_version:=v_supplier_source.get_number('stock_version');RRL_STOCK_SUP_RETURN.declare_source(v_supplier_source,p_operation,r);end if;
  end if;
"""+needle,1)
needle="   if v_return_supplier is not null then"
# The generic free-stock branch below gets a pinned supplier source branch before the old RETURNS fallback.
at=s.index(needle,s.index("  for i in 0..a.get_size-1 loop"))
s=s[:at]+"""   if v_supplier_source is not null then
    if a.get_size!=1 or v_article!=v_supplier_source.get_string('article')or v_base!=v_supplier_source.get_string('base_uom')or v_qty!=RRL_STOCK_MATH.quantity(v_supplier_source.get_string('quantity'))then raise_application_error(-20886,'SUP_RETURN_EXISTING_ST_WHOLE_SOURCE_COMPOSITION_REQUIRED');end if;
    v_cell:=v_supplier_source.get_string('cell');v_version:=v_supplier_source.get_number('uom_version');
    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_bound_uid,v_article,v_cell,null);
    leg:=json_object_t();leg.put('row_id',l.get_number('id'));leg.put('uid',v_bound_uid);leg.put('cell',v_cell);leg.put('article',v_article);leg.put('source_p',v_supplier_source.get_string('quantity'));leg.put('quantity',v_supplier_source.get_string('quantity'));leg.put('base_uom',v_base);leg.put('uom_version',v_version);legs.append(leg);v_qty:=0;
   else
"""+s[at:]
needle="   if v_qty>0 then raise_application_error(-20868,'SHIPMENT_AVAILABLE_STOCK_INSUFFICIENT');end if;"
assert needle in s;s=s.replace(needle,needle+"\n   end if;",1)
s=s.replace("  v.put('bound_physical_uid'","  if v_supplier_source is not null then v.put('supplier_return_source',v_supplier_source);end if;\n  v.put('bound_physical_uid'",1)
s=s.replace("  if v.get_string('bound_physical_uid') is not null then","  if v.get_string('bound_physical_uid') is not null and not v.has('supplier_return_source') then",1)
# Exact typed receipt is passed to the same consumption primitive.
needle="case when v_kind='SHIP_PALLET' then v_row_id end);"
assert needle in s;s=s.replace(needle,"case when v_kind='SHIP_PALLET' then v_row_id end,case when v.has('supplier_return_source') then v.get_object('supplier_return_source').get_string('receipt_operation_id')end);",1)
# Execute_resolved final result prefix, after effects and before commit.
needle="  p_result:=j.to_clob;"
assert needle in s;s=s.replace(needle,"  if v.has('supplier_return_source')then RRL_STOCK_SUP_RETURN.dispatched(v.get_object('supplier_return_source'),p_actor);end if;\n"+needle,1)
out[str(f/"003_shipping.sql")]=s
s=Path("db/migrations/2026-10-08_stock_posting_core/424_before108_effect.sql").read_text(encoding="utf-8-sig").replace("p_pallet_row number default null","p_pallet_row number default null,p_supplier_return_receipt varchar2 default null")
s=s.replace("  RRL_STOCK_LOCATION_CORE.assert_ordinary(p_cell,p_warehouse,'SOURCE');","""  if p_supplier_return_receipt is null then RRL_STOCK_LOCATION_CORE.assert_ordinary(p_cell,p_warehouse,'SOURCE');
  else RRL_STOCK_SUP_RETURN.validate_consume(p_supplier_return_receipt,p_uid,p_cell,p_qty,p_warehouse,p_actor);RRL_STOCK_LOCATION_CORE.assert_quarantine(p_cell,p_warehouse);end if;""",1);out[str(f/"004_effect.sql")]=s
out[str(f/"005_guards.sql")]=r"""create or replace trigger RRL_SUP_RETURN_BIND_GUARD before insert or update or delete on RRL_STORE_RETURN_SUP_BIND for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'SUP_RETURN_SOURCE_HISTORY_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if RRL_HAS_WRIGHT(:new.ACTOR,'store_return_approve')!=1 or RRL_HAS_WRIGHT(:new.ACTOR,'outgoing_pallet_edit')!=1 then raise_application_error(-20882,'SUP_RETURN_APPROVED_PREPARATION_REQUIRED');end if;
 select count(*)into n from RRL_SBORKA_PALLETS where ID=:new.ST_ID and PALLET_UID=:new.ST_IDENTIFIER and RETURN_SUPPLIER_ID=:new.SUPPLIER_INN;
 if n!=1 then raise_application_error(-20886,'SUP_RETURN_EXISTING_ST_IDENTITY_REQUIRED');end if;
end;
/
create or replace trigger RRL_SUP_RETURN_DISPATCH_GUARD before insert or update or delete on RRL_STORE_RETURN_SUP_DISPATCH for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'SUP_RETURN_DISPATCH_HISTORY_IMMUTABLE');end if;
 if op is null or :new.OPERATION_ID!=op or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'SUP_RETURN_DISPATCH_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='LOAD_SHIPMENT'or v_state!='IN_FLIGHT'then raise_application_error(-20863,'SUP_RETURN_ACTUAL_LOADING_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RETURN_SUP_DISPATCH',op));
end;
/
"""
out[str(f/"apply.sql")]="\n".join("@@"+n for n in ["001_schema.sql","002_helper.sql","004_effect.sql","003_shipping.sql","005_guards.sql"])+r"""
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_SUP_RETURN','RRL_STOCK_SHIPPING_CORE','RRL_STOCK_EFFECT_CORE','RRL_SUP_RETURN_BIND_GUARD','RRL_SUP_RETURN_DISPATCH_GUARD')and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'SUP_RETURN_DISPATCH_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-108-supplier-return-existing-loading' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing PALL_SPLITTER supplier ST pins actual placed store return; existing single physical load/current QC/core consumes exactly one segregated pallet and records dispatch, not supplier receipt',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
"""
out[str(f/"rollback.sql")]=r"""declare n number;begin select count(*)into n from RRL_STORE_RETURN_SUP_DISPATCH;if n>0 then raise_application_error(-20808,'SUP_RETURN_DISPATCH_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/423_before108_shipping.sql
@@../2026-10-08_stock_posting_core/424_before108_effect.sql
"""
for name in ["001_schema.sql","002_helper.sql","003_shipping.sql","004_effect.sql","005_guards.sql","apply.sql","rollback.sql"]:
 out[str(f/name)]=(f/name).read_text(encoding="utf-8-sig")
print(json.dumps(out,ensure_ascii=True))
