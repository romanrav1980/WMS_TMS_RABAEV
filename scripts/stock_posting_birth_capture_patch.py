"""Add trusted mark staging inside the existing coordinator transaction."""
import json
from pathlib import Path
d=Path("db/migrations/2026-10-08_stock_posting_core");out={}
p=d/"024_posting.sql";s=p.read_text(encoding="utf-8")
s=s.replace(" procedure reset_connection;"," procedure stage_birth(p_uid varchar2);\n procedure finish_birth_capture;\n procedure reset_connection;",1)
needle="  RRL_STOCK_LOCK_API.begin_plan;\n  RRL_STOCK_LOCK_API.acquire_policies(v_policies);"
assert s.count(needle)==1
s=s.replace(needle,"""  if v_domain is not null and p_hints is not null and g_kind in('INVENTORY_REGISTER_LOT','MES_MOVEMENTS') then
   declare h json_object_t:=json_object_t.parse(p_hints);a json_array_t;b json_object_t;u json_object_t;
    rr json_array_t:=json_array_t.parse(v_resources);dom json_object_t:=json_object_t.parse(v_domain);
    uid varchar2(150);qty varchar2(30);base varchar2(20);cell varchar2(60);found boolean;total number;
   begin
    a:=h.get_array('births');if a.get_size>200 then raise_application_error(-20881,'BIRTH_CAPTURE_BOUND');end if;
    for i in 0..a.get_size-1 loop
     b:=treat(a.get(i) as json_object_t);uid:=b.get_string('uid');found:=false;
     if g_kind='INVENTORY_REGISTER_LOT' and dom.get_string('uid')=uid then
      found:=true;qty:=dom.get_string('quantity');base:=dom.get_string('base');cell:=dom.get_string('cell');
     elsif g_kind='MES_MOVEMENTS' then
      for z in 0..dom.get_array('movements').get_size-1 loop
       u:=treat(dom.get_array('movements').get(z) as json_object_t);
       if u.get_string('physical_uid')=uid and u.get_number('movement_id')=b.get_number('movement_id') then
        declare m RRL_MES_MOVEMENT%rowtype;mid number:=u.get_number('movement_id');begin
         select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=mid;
         if m.MOVEMENT_TYPE!='FG_PALLET_RELEASE' then raise_application_error(-20884,'NOT_A_BIRTH_MOVEMENT');end if;
         found:=true;qty:=u.get_string('base_quantity');base:=u.get_string('base_uom');cell:=m.TARGET_LOCATION;
        end;
       end if;
      end loop;
     end if;
     if not found or b.get_string('quantity')!=qty or b.get_string('base')!=base or b.get_string('cell')!=cell
      then raise_application_error(-20890,'CLOSURE_CHANGED: birth capture');end if;
     total:=0;
     if b.get_array('unit_bindings').get_size<1 or b.get_array('unit_bindings').get_size>10000 then raise_application_error(-20881,'BIRTH_UNIT_BOUND');end if;
     for z in 0..b.get_array('unit_bindings').get_size-1 loop
      u:=treat(b.get_array('unit_bindings').get(z) as json_object_t);
      total:=total+RRL_STOCK_MATH.quantity(u.get_string('quantity'));
      RRL_STOCK_PLAN_HELPER.anchor(rr,60,'UNIT',u.get_string('key'));
     end loop;
     if total!=RRL_STOCK_MATH.quantity(qty) then raise_application_error(-20884,'BIRTH_UNIT_QUANTITY_CONFLICT');end if;
     for z in 0..b.get_array('aliases').get_size-1 loop
      u:=treat(b.get_array('aliases').get(z) as json_object_t);
      RRL_STOCK_PLAN_HELPER.anchor(rr,70,'UNIQUE','MARK:'||u.get_string('system')||':'||u.get_string('hash'));
     end loop;
    end loop;
    v_resources:=rr.to_clob;v_resolution.put('births',a);
   end;
  end if;
"""+needle,1)
needle=" procedure execute_prepared(p_result out clob) is"
assert s.count(needle)==1
stage=""" procedure stage_birth(p_uid varchar2) is
  d json_object_t:=json_object_t.parse(g_resolution);b json_object_t;v json_object_t;a json_array_t;
  n number;policy number;found boolean:=false;uid varchar2(150);article varchar2(160);cell varchar2(60);qty number;
  doc number;expiry date;price number;mid number;m RRL_MES_MOVEMENT%rowtype;
 begin
  if not g_prepared or g_tx is null or g_tx!=dbms_transaction.local_transaction_id(false)
   or g_kind not in('INVENTORY_REGISTER_LOT','MES_MOVEMENTS') then raise_application_error(-20850,'WRITE_PLAN_VIOLATION');end if;
  if RRL_HAS_WRIGHT(g_actor,case when g_kind='INVENTORY_REGISTER_LOT' then 'stock_inventory_count' else 'mes_apply_wms' end)!=1
   then raise_application_error(-20882,'BIRTH_CAPTURE_FORBIDDEN');end if;
  a:=d.get_array('births');
  for i in 0..a.get_size-1 loop
   b:=treat(a.get(i) as json_object_t);
   if b.get_string('uid')=p_uid then found:=true;exit;end if;
  end loop;
  if not found then raise_application_error(-20884,'BIRTH_CAPTURE_NOT_PLANNED');end if;
  uid:=b.get_string('uid');article:=b.get_string('article');cell:=b.get_string('cell');qty:=RRL_STOCK_MATH.quantity(b.get_string('quantity'));
  select POLICY_VERSION into policy from RRL_SKU_RECEIPT_POLICY where ARTICUL=article and MARKING_REQUIRED=1;
  if policy!=b.get_number('policy_version') then raise_application_error(-20890,'CLOSURE_CHANGED: birth marking policy');end if;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',uid));
  select count(*) into n from RRL_REMAINS where UID_POLETA=uid and REMAIN>0;
  if n>0 then raise_application_error(-20886,'BIRTH_STOCK_ALREADY_EXISTS');end if;
  select count(*) into n from RRL_PALLETS where UID_PALLET=uid;
  if n=0 then
   if g_kind='INVENTORY_REGISTER_LOT' then
    v:=d.get_object('domain');doc:=v.get_number('document');expiry:=to_date(v.get_string('expiry_date'),'FXYYYY-MM-DD');price:=v.get_number('price');
    insert into RRL_PALLETS(UID_PALLET,ARTICUL,CREATION_DATE,EXPIRY_DATE,UNIT_COUNT,PRICE,PRIHOD_NAKLAD_ID,STOCK_ORIGIN_UID,CREATED_BY_STOCK_OP)
     values(uid,article,systimestamp,expiry,qty,price,-doc,uid,g_operation);
   else
    mid:=b.get_number('movement_id');select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=mid;
    insert into RRL_PALLETS(UID_PALLET,ARTICUL,UNIT_COUNT,PRIHOD_NAKLAD_ID,PROD_BATCH_ID,SSCC,QUALITY_STATUS,CREATED_BY_STOCK_OP)
     values(uid,article,qty,0,m.PROD_BATCH_ID,m.SSCC,'RELEASED',g_operation);
   end if;
  end if;
  RRL_STOCK_CTX_API.begin_staging(uid,cell);
 end;
 procedure finish_birth_capture is
 begin
  if not g_prepared or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,'WRITE_PLAN_VIOLATION');end if;
  RRL_STOCK_CTX_API.end_effect;
 end;
"""
s=s.replace(needle,stage+needle,1)
out[str(p)]=s
p=d/"125_inventory_birth.sql";s=p.read_text(encoding="utf-8")
s=s.replace("  if marked!=0 then raise_application_error(-20884,'MARKED_INVENTORY_CAPTURE_REQUIRED');end if;","",1)
needle="  if n>0 then raise_application_error(-20887,'INVENTORY_PALLET_ALREADY_EXISTS: use measured count for existing identity');end if;"
assert s.count(needle)==1
s=s.replace(needle,"""  if n>0 then
   declare v_owner varchar2(100);v_op varchar2(100):=d.get_string('operation_id');begin
    select CREATED_BY_STOCK_OP into v_owner from RRL_PALLETS where UID_PALLET=uid;
    if v_owner is null or v_owner!=v_op then raise_application_error(-20887,'INVENTORY_PALLET_ALREADY_EXISTS: use measured count');end if;
   end;
  end if;""",1)
# Staged marked birth already owns the pallet. Keep ordinary unmarked creation unchanged.
s=s.replace("insert into RRL_PALLETS(UID_PALLET,ARTICUL,CREATION_DATE", "if n=0 then insert into RRL_PALLETS(UID_PALLET,ARTICUL,CREATION_DATE",1)
s=s.replace("values(uid,article,systimestamp,expiry,qty,price,-doc,uid,v_json_sql_1_1);","values(uid,article,systimestamp,expiry,qty,price,-doc,uid,v_json_sql_1_1);end if;",1)
needle="  RRL_STOCK_BALANCE_CORE.write_leg(uid,null,cell,qty,base,version,1,1,1,p_actor,eventid);"
assert s.count(needle)==1
s=s.replace(needle,"  RRL_STOCK_UNIT_CORE.assert_composition(uid,cell);\n"+needle,1)
# n is reused by cell checks; independently determine if a staged pallet exists before insert.
s=s.replace("if n=0 then insert into RRL_PALLETS","select count(*) into n from RRL_PALLETS where UID_PALLET=uid;\nif n=0 then insert into RRL_PALLETS",1)
out[str(p)]=s
p=d/"039_unit_core.sql";s=p.read_text(encoding="utf-8")
s=s.replace("accessible by(","accessible by(package RRL_STOCK_INVENTORY_BIRTH,",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/birth_capture.py");s=p.read_text(encoding="utf-8")
s=s.replace('    cursor.execute("begin RRL_STOCK_POSTING_API.stage_births; end;")\n',"",1)
s=s.replace('begin RRL_STOCK_CTX_API.begin_staging(:uid,:cell); end;','begin RRL_STOCK_POSTING_API.stage_birth(:uid); end;').replace('uid=birth["uid"],cell=birth["cell"]','uid=birth["uid"]')
s=s.replace("begin RRL_STOCK_CTX_API.end_effect; end;","begin RRL_STOCK_POSTING_API.finish_birth_capture; end;")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py");s=p.read_text(encoding="utf-8")
s=s.replace("cell: str | None = None) -> None:","cell: str | None = None, source_kind: str = 'PHYSICAL_RECEIPT') -> None:",1)
s=s.replace("'physical_receipt': True","'physical_receipt': source_kind == 'PHYSICAL_RECEIPT'",1)
s=s.replace("'p_operation_type': 'PHYSICAL_RECEIPT'","'p_operation_type': source_kind",1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py");s=p.read_text(encoding="utf-8")
s=s.replace("        receipt_marks = None","        birth_captures = {}\n        receipt_marks = None",1)
needle="        posting_started = True"
assert s.count(needle)==1
s=s.replace(needle,"""        if command_document["command_type"] in {"INVENTORY_REGISTER_LOT","MES_MOVEMENTS"}:
            cursor.execute("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:i",i=operation_id)
            if cursor.fetchone() is None:
                from .birth_capture import plan_births
                try:
                    hints,birth_captures=plan_births(cursor,command_document)
                    resolution=json.dumps(hints,ensure_ascii=True,separators=(",",":"),allow_nan=False)
                except Exception:
                    cursor.execute("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:i",i=operation_id)
                    if cursor.fetchone() is None:raise
"""+needle,1)
needle='            cursor.execute("begin RRL_STOCK_POSTING_API.execute_prepared(:result); end;", {"result": result})'
assert s.count(needle)==1
s=s.replace(needle,"""            if birth_captures:
                from .birth_capture import stage_births
                stage_births(cursor,command_document,birth_captures)
"""+needle,1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
