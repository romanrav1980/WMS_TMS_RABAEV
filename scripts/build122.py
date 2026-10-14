from pathlib import Path
import json,re
base=Path("db/migrations/2026-10-08_stock_posting_core");dest="db/migrations/2026-10-10_ni061_onward/";out={}
s=(base/"440_before122_shipping.sql").read_text(encoding="utf-8");s=re.sub(r"\n\s*\n","\n",s)
s=s.replace("v_supplier_source json_object_t;","v_supplier_source json_object_t;v_interware_source json_object_t;",1)
needle="  if v_return_supplier is not null then\n   v_supplier_source:="
assert needle in s
extra="""  if v_kind='SHIP_PALLET' then
   v_interware_source:=RRL_STOCK_INTERWARE_NEXT.describe_source(v_id,v_ware);
   if v_interware_source is not null then
    if v_customer_order is not null or v_return_supplier is not null then raise_application_error(-20886,'INTERWARE_ONWARD_NO_DUPLICATE_CUSTOMER_FULFILLMENT');end if;
    v_bound_uid:=v_interware_source.get_string('uid');v_bound_version:=v_interware_source.get_number('stock_version');RRL_STOCK_INTERWARE_NEXT.declare_source(v_interware_source,p_operation,r);
   end if;
  end if;
"""
s=s.replace(needle,extra+needle,1)
needle="   if v_supplier_source is not null then\n    v_base:="
assert needle in s
extra="""   if v_interware_source is not null then
    v_base:=v_interware_source.get_string('base_uom');
    if nvl(l.get_string('input_uom'),'~')!=v_base or a.get_size!=1 or v_article!=v_interware_source.get_string('article')or v_qty!=RRL_STOCK_MATH.quantity(v_interware_source.get_string('quantity'))then raise_application_error(-20886,'INTERWARE_ONWARD_EXISTING_ST_EXACT_BASE_COMPOSITION_REQUIRED');end if;
    v_cell:=v_interware_source.get_string('cell');v_version:=v_interware_source.get_number('uom_version');
    RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_bound_uid,v_article,v_cell,null);
    leg:=json_object_t();leg.put('row_id',l.get_number('id'));leg.put('uid',v_bound_uid);leg.put('cell',v_cell);leg.put('article',v_article);leg.put('source_p',v_interware_source.get_string('quantity'));leg.put('quantity',v_interware_source.get_string('quantity'));leg.put('base_uom',v_base);leg.put('uom_version',v_version);legs.append(leg);v_qty:=0;
   elsif v_supplier_source is not null then
    v_base:="""
s=s.replace(needle,extra,1)
needle="  if v_supplier_source is not null then v.put('supplier_return_source',v_supplier_source);end if;"
assert needle in s;s=s.replace(needle,"  if v_interware_source is not null then v.put('interwarehouse_onward_source',v_interware_source);end if;\n"+needle,1)
s=s.replace("and not v.has('supplier_return_source') then","and not v.has('supplier_return_source') and not v.has('interwarehouse_onward_source') then",1)
needle="  a:=v.get_array('legs');"
assert needle in s
s=s.replace(needle,"  if v.has('interwarehouse_onward_source')then RRL_STOCK_INTERWARE_NEXT.validate_load(v.get_object('interwarehouse_onward_source'),p_actor);end if;\n"+needle,1)
needle="  if v.has('supplier_return_source')then RRL_STOCK_SUP_RETURN.dispatched"
assert needle in s;s=s.replace(needle,"  if v.has('interwarehouse_onward_source')then RRL_STOCK_INTERWARE_NEXT.dispatched(v.get_object('interwarehouse_onward_source'),p_actor);end if;\n"+needle,1)
out[dest+"003_shipping.sql"]=s
out[dest+"004_guards.sql"]="""create or replace trigger RRL_INTERWARE_ONWARD_BIND_GUARD before insert or update or delete on RRL_INTERWARE_ONWARD_BIND for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_ONWARD_BIND_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'INTERWARE_ONWARD_METADATA_ACTOR_REQUIRED');end if;
 select count(*)into n from RUSERS u where ID=:new.ACTOR and nvl(DELETED,0)=0 and(WARE_ID=:new.WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'outgoing_pallet_edit')=1 and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1;
 if n!=1 then raise_application_error(-20882,'INTERWARE_ONWARD_WARE_DISPATCHER_REQUIRED');end if;
 select count(*)into n from RRL_INTERWARE_RECEIPT r join RRL_INTERWARE_PLAN p on p.OPERATION_ID=r.PLAN_OPERATION_ID join RRL_INTERWARE_PLACEMENT x on x.RECEIPT_OPERATION_ID=r.OPERATION_ID join RRL_INTERWARE_CUSTODY_PROOF c on c.RECEIPT_OPERATION_ID=r.OPERATION_ID
 join RRL_REMAINS stock on stock.UID_POLETA=r.ROOT_UID and stock.CELL=x.TARGET_CELL
 join RRL_TT_HU_LOAD_ST member on member.LOAD_OPERATION_ID=p.SOURCE_LOAD_OPERATION_ID and member.SBORKA_PALLET_ID=p.SOURCE_ST_ID
 where r.OPERATION_ID=:new.RECEIPT_OPERATION_ID and r.ROOT_UID=:new.ROOT_UID and r.WARE_ID=:new.WARE_ID and p.SOURCE_ST_ID=:new.SOURCE_ST_ID and p.SOURCE_LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID and p.TARGET_TT_ID=:new.TARGET_TT_ID and member.DESTINATION_ADDR=:new.FINAL_ADDRESS and x.TARGET_CELL=:new.SOURCE_CELL and stock.STOCK_VERSION=:new.STOCK_VERSION and stock.REMAIN=r.BASE_QTY and stock.HARD_RESERVED_BASE=0 and stock.BASE_UOM=r.BASE_UOM;
 if n!=1 then raise_application_error(-20886,'INTERWARE_ONWARD_ORIGINAL_PLACED_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_SBORKA_PALLETS s where s.ID=:new.ST_ID and s.PALLET_UID=:new.ST_IDENTIFIER and s.WARE_ID=:new.WARE_ID and s.RETURN_SUPPLIER_ID is null and s.ADDR=:new.FINAL_ADDRESS and nvl(s.CONDITION,0)<2 and s.TRANSTASK_ID is null;
 if n!=1 then raise_application_error(-20886,'INTERWARE_ONWARD_EXISTING_CONSTRUCTOR_REQUIRED');end if;
end;
/
create or replace trigger RRL_INTERWARE_ONWARD_FACT_GUARD before insert or update or delete on RRL_INTERWARE_ONWARD_DISPATCH for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_ONWARD_FACT_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_ONWARD_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='LOAD_SHIPMENT'and STATE='IN_FLIGHT'and ACTOR=:new.ACTOR and json_value(RESOLVED_PLAN_JSON,'$.domain.shipment.domain.interwarehouse_onward_source.binding_operation_id')=:new.BIND_OPERATION_ID;
 if n!=1 then raise_application_error(-20863,'INTERWARE_ONWARD_ORIGINAL_LOADING_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_ONWARD_DISPATCH',op));
end;
/
create or replace trigger RRL_INTERWARE_ONWARD_ST_GUARD before update or delete on RRL_SBORKA_PALLETS for each row
declare n number;t number;
begin
 select count(*),max(TARGET_TT_ID)into n,t from RRL_INTERWARE_ONWARD_BIND where ST_ID=:old.ID;if n=0 then return;end if;
 if deleting then raise_application_error(-20863,'INTERWARE_ONWARD_ST_PRESERVE');end if;
 if :new.ID!=:old.ID or :new.PALLET_UID!=:old.PALLET_UID or :new.WARE_ID!=:old.WARE_ID or :new.ADDR!=:old.ADDR or nvl(:new.ST_NUMBER,chr(0))!=nvl(:old.ST_NUMBER,chr(0))or :new.RETURN_SUPPLIER_ID is not null then raise_application_error(-20863,'INTERWARE_ONWARD_ST_SOURCE_IMMUTABLE');end if;
 if :new.TRANSTASK_ID is not null and :new.TRANSTASK_ID!=t then raise_application_error(-20886,'INTERWARE_ONWARD_ONLY_ORIGINAL_TARGET_TRIP');end if;
end;
/
create or replace trigger RRL_INTERWARE_ONWARD_ROW_GUARD before insert or update of PALLET_UID,ARTICUL,QUANTITY,EI or delete on RRL_SBORKA_PALLET_ROWS for each row
declare n number;
begin
 select count(*)into n from RRL_INTERWARE_ONWARD_BIND where ST_IDENTIFIER in(:old.PALLET_UID,:new.PALLET_UID);if n=0 then return;end if;
 if inserting or deleting then raise_application_error(-20863,'INTERWARE_ONWARD_ST_ROWS_IMMUTABLE');end if;
 if nvl(:new.PALLET_UID,chr(0))!=nvl(:old.PALLET_UID,chr(0))or nvl(:new.ARTICUL,chr(0))!=nvl(:old.ARTICUL,chr(0))or nvl(:new.QUANTITY,-1)!=nvl(:old.QUANTITY,-1)or nvl(:new.EI,chr(0))!=nvl(:old.EI,chr(0))then raise_application_error(-20863,'INTERWARE_ONWARD_ST_ROWS_IMMUTABLE');end if;
end;
/
"""
out[dest+"apply.sql"]="""@@001_schema.sql
@@002_helper.sql
@@003_shipping.sql
@@004_guards.sql
declare n number;begin select count(*)into n from user_objects where OBJECT_NAME in('RRL_STOCK_INTERWARE_NEXT','RRL_STOCK_SHIPPING_CORE','RRL_INTERWARE_ONWARD_BIND_GUARD','RRL_INTERWARE_ONWARD_FACT_GUARD','RRL_INTERWARE_ONWARD_ST_GUARD','RRL_INTERWARE_ONWARD_ROW_GUARD')and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'INTERWARE122_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-122-existing-onward-st-original-ownership' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing ordinary ST constructor/rows and exact source-pinned second shoulder loading, original customer ownership retained without new fulfillment',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
"""
out[dest+"rollback.sql"]="""declare n number;begin select count(*)into n from RRL_INTERWARE_ONWARD_BIND;if n!=0 then raise_application_error(-20899,'INTERWARE122_FACTS_FORWARD_ONLY');end if;end;
/
drop trigger RRL_INTERWARE_ONWARD_ROW_GUARD;
drop trigger RRL_INTERWARE_ONWARD_ST_GUARD;
@@../2026-10-08_stock_posting_core/440_before122_shipping.sql
drop table RRL_INTERWARE_ONWARD_DISPATCH;
drop table RRL_INTERWARE_ONWARD_BIND;
drop package RRL_STOCK_INTERWARE_NEXT;
"""
# Final source overrides keep applied incremental refinements.
for name in ['001_schema.sql','003_shipping.sql','004_guards.sql','apply.sql','rollback.sql']:
 out[dest+name]=Path(dest+name).read_text(encoding='utf-8')
print(json.dumps(out,ensure_ascii=True))
