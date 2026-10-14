from pathlib import Path
import json,hashlib
before=Path("tmp/741_st_defer_before.sql").read_text(encoding="utf-8")
d="db/migrations/2026-10-12_ni072_prepared_st_deferral";out={}
out[d+"/000_before.sql"]=before
out[d+"/001_physical.sql"]="""create or replace package RRL_ST_DEFER_PHYSICAL authid definer accessible by(package RRL_ST_DEFER_API)as
 function snapshot(p_st varchar2,p_ware number)return clob;
end;
/
create or replace package body RRL_ST_DEFER_PHYSICAL as
 function snapshot(p_st varchar2,p_ware number)return clob is
  n number;bad number;expected number;counted number:=0;items json_array_t:=json_array_t();item json_object_t;result json_object_t:=json_object_t();
 begin
  select count(*),sum(case when nvl(f.FACT_QTY,0)>0 then 1 else 0 end)into expected,n
   from RRL_CUSTOMER_ORDER_FULFILLMENT f join RRL_SBORKA_PALLETS p on p.ID=f.LEGACY_SBORKA_PALLET_ID where p.ST_NUMBER=p_st;
  if nvl(n,0)=0 then result.put('state','UNPICKED');return result.to_clob;end if;
  if expected>200 then raise_application_error(-20881,'ST_DEFER_PREPARED_MEMBER_BOUND_200');end if;
  select count(*)into bad from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS p on p.ID=c.LEGACY_SBORKA_PALLET_ID where p.ST_NUMBER=p_st;
  if bad!=0 then raise_application_error(-20886,'ST_DEFER_PREPARED_CASE_DECISION_REQUIRED');end if;
  for x in(select f.FULFILLMENT_ID,f.LEGACY_SBORKA_PALLET_ID,f.STATUS,f.FACT_QTY,f.FACT_UOM,f.PICKED_PALLET_UID,
    f.PICKED_CASE_TASK_ID,f.PICKED_WAREHOUSE_TASK_ID,f.PICKED_OPERATION_ID,f.PICKED_STOCK_VERSION,
    t.STATUS TASK_STATUS,t.TASK_TYPE,t.TO_WARE_ID,t.TO_CELL,nvl(t.TARGET_UID_PALLET,t.UID_PALLET)TASK_UID,
    r.REMAIN,r.HARD_RESERVED_BASE,r.BASE_UOM,r.STOCK_VERSION,cell.WARE_ID CELL_WARE
   from RRL_CUSTOMER_ORDER_FULFILLMENT f join RRL_SBORKA_PALLETS p on p.ID=f.LEGACY_SBORKA_PALLET_ID
   left join RRL_WAREHOUSE_TASK t on t.TASK_ID=f.PICKED_WAREHOUSE_TASK_ID
   left join RRL_REMAINS r on r.UID_POLETA=f.PICKED_PALLET_UID and r.CELL=t.TO_CELL
   left join RRL_CELLS cell on cell.CELL=t.TO_CELL where p.ST_NUMBER=p_st order by f.FULFILLMENT_ID)loop
   if x.STATUS!='PICKED'or nvl(x.FACT_QTY,0)<=0 or x.PICKED_CASE_TASK_ID is not null or x.PICKED_WAREHOUSE_TASK_ID is null
    or x.PICKED_OPERATION_ID is null or nvl(x.TASK_STATUS,'NONE')!='DONE'or nvl(x.TASK_TYPE,'NONE')!='PICKING_MOVE'
    or nvl(x.TO_WARE_ID,-1)!=p_ware or nvl(x.CELL_WARE,-1)!=p_ware or x.PICKED_PALLET_UID is null
    or nvl(x.TASK_UID,'NONE')!=x.PICKED_PALLET_UID or nvl(x.REMAIN,-1)!=x.FACT_QTY or nvl(x.HARD_RESERVED_BASE,-1)!=x.FACT_QTY
    or x.FACT_UOM is null or nvl(x.BASE_UOM,'NONE')!=x.FACT_UOM then raise_application_error(-20886,'ST_DEFER_WHOLE_PREPARED_STOCK_REQUIRED');end if;
   select count(*)into bad from RRL_WMS_HU_LINK h where h.ACTIVE_FLAG=1 and(h.CHILD_PALLET_UID=x.PICKED_PALLET_UID or h.PARENT_PALLET_UID=x.PICKED_PALLET_UID);
   if bad!=0 then raise_application_error(-20886,'ST_DEFER_PREPARED_NESTED_DECISION_REQUIRED');end if;
   select count(*)into bad from RRL_WAREHOUSE_TASK w where w.STATUS not in('DONE','CANCELLED')and(w.UID_PALLET=x.PICKED_PALLET_UID or w.TARGET_UID_PALLET=x.PICKED_PALLET_UID);
   if bad!=0 then raise_application_error(-20886,'ST_DEFER_PREPARED_PHYSICAL_TASK_OPEN');end if;
   item:=json_object_t();item.put('fulfillment_id',x.FULFILLMENT_ID);item.put('st_member_id',x.LEGACY_SBORKA_PALLET_ID);
   item.put('pallet_identifier',x.PICKED_PALLET_UID);item.put('cell',x.TO_CELL);item.put('task_id',x.PICKED_WAREHOUSE_TASK_ID);
   item.put('picked_operation_id',x.PICKED_OPERATION_ID);item.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(x.FACT_QTY));
   item.put('base_uom',x.FACT_UOM);item.put('stock_version',x.STOCK_VERSION);item.put('picked_stock_version',x.PICKED_STOCK_VERSION);items.append(item);counted:=counted+1;
  end loop;
  if counted!=expected or counted<1 then raise_application_error(-20886,'ST_DEFER_EXACT_PREPARED_MEMBERS_REQUIRED');end if;
  select count(*)into bad from RRL_SBORKA_PALLETS p where p.ST_NUMBER=p_st and not exists(select 1 from RRL_CUSTOMER_ORDER_FULFILLMENT f where f.LEGACY_SBORKA_PALLET_ID=p.ID);
  if bad!=0 then raise_application_error(-20886,'ST_DEFER_MIXED_PREPARED_UNPICKED_REQUIRED');end if;
  result.put('state','PREPARED_WHOLE_STOCK');result.put('members',items);result.put('physical_move_required',true);result.put('stock_changed',false);return result.to_clob;
 end;
end;
/
"""
after=before
anchor="  p_json:=b.to_clob;p_hash:="
add="  declare prepared json_object_t:=json_object_t.parse(RRL_ST_DEFER_PHYSICAL.snapshot(p_st,p_ware));begin if prepared.get_string('state')!='UNPICKED'then b.put('physical_preparation',prepared);end if;end;\n"
assert after.count(anchor)==1;after=after.replace(anchor,add+anchor)
old="""or exists(select 1 from RRL_CUSTOMER_ORDER_FULFILLMENT f where f.LEGACY_SBORKA_PALLET_ID=p.ID and(nvl(f.FACT_QTY,0)>0 or f.PICKED_CASE_TASK_ID is not null))"""
assert after.count(old)==1;after=after.replace(old,"or exists(select 1 from RRL_CUSTOMER_ORDER_FULFILLMENT f where f.LEGACY_SBORKA_PALLET_ID=p.ID and f.PICKED_CASE_TASK_ID is not null)")
after=after.replace("ST_DEFER_UNPICKED_UNLOADED_ONLY","ST_DEFER_UNLOADED_SUPPORTED_PHYSICAL_SOURCE_ONLY")
needle="  result.put('assignment',json_object_t.parse(assigned));"
assert after.count(needle)==1
after=after.replace(needle,"  if json_object_t.parse(src).has('physical_preparation')then result.put('physical_preparation',json_object_t.parse(src).get_object('physical_preparation'));end if;\n"+needle)
out[d+"/002_api.sql"]=after
out[d+"/apply.sql"]="@@001_physical.sql\n@@002_api.sql\n@@003_ledger.sql\n"
out[d+"/rollback.sql"]="@@000_before.sql\ndrop package RRL_ST_DEFER_PHYSICAL;\n"
out[d+"/verify.sql"]="select *from USER_ERRORS where NAME in('RRL_ST_DEFER_API','RRL_ST_DEFER_PHYSICAL');\n"
out[d+"/003_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-743-prepared-st-deferral'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing ST deferral supports whole completed flat stock picks; original quantity and reservation retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
out[d+"/checkpoint.json"]=json.dumps({"schema":"RABAEV","service":"orcl","before_sha256":hashlib.sha256(before.encode()).hexdigest(),"scope":"metadata only; fully picked flat warehouse-task sources; CASE/nested/onward not admitted","recovery":"restore existing API body and drop additive helper; immutable histories preserved"},indent=2)
p=Path("wiki-raw/wms_admin_ui_reference/st-deferral.js");s=p.read_text(encoding="utf-8").replace("Перенос разрешается только до отбора и погрузки.","Перенос разрешается только до погрузки. Полный отбор плоских товарных паллет сохраняется; CASE и вложенные места требуют отдельного решения.")
s=s.replace("'. Исходная дата рейса '+v.source_trip.shipment_date+", "'. Исходная дата рейса '+v.source_trip.shipment_date+")
s=s.replace("контекст", "контекст")
needle=";controls();\n  }catch"
s=s.replace(needle,";if(v.physical_preparation)el('sdMessage').textContent+=' Товар уже отобран: перенос рейса не перемещает его. Создайте штатное складское задание в зону ожидания.';controls();\n  }catch",1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
