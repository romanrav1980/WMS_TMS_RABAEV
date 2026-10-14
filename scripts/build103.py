from pathlib import Path
import json
out={};folder=Path("db/migrations/2026-10-10_ni063_fullpal_tare")
p=Path("db/migrations/2026-10-10_ni063_tare_assembly/003_command.sql");s=p.read_text(encoding="utf-8-sig")
s=s.replace("v_book varchar2(100);","v_book varchar2(100);v_goods_kind varchar2(20);v_article varchar2(100);v_stock_version number;",1)
old="""  if pp.HU_KIND!='CONTAINER' or pp.HU_CURRENT_CELL is null or pp.HU_TYPE not in('PALLET','ROLL_CAGE')then raise_application_error(-20886,'TARE_RETURNABLE_CURRENT_CONTAINER_REQUIRED');end if;
  v_cell:=pp.HU_CURRENT_CELL;v_content:=pp.HU_CONTENT_VERSION;v_status:=pp.HU_TYPE;
  select WARE_ID into v_ware from RRL_CELLS where CELL=v_cell;
  select LOAD_UNIT_CLASS into v_class from RRL_PALLET_TYPE where PALLET_TYPE_ID=v_type and ACTIVE=1;
  if(pp.HU_TYPE='PALLET' and v_class!='PALLET')or(pp.HU_TYPE='ROLL_CAGE' and v_class!='TROLLEY')then raise_application_error(-20886,'TARE_CONTAINER_PHYSICAL_TYPE_CONFLICT');end if;"""
new="""  v_goods_kind:=nvl(pp.HU_KIND,'STOCK');v_article:=pp.ARTICUL;
  v_content:=pp.HU_CONTENT_VERSION;
  if v_goods_kind='CONTAINER' then
   if pp.HU_CURRENT_CELL is null or pp.HU_TYPE not in('PALLET','ROLL_CAGE')then raise_application_error(-20886,'TARE_RETURNABLE_CURRENT_CONTAINER_REQUIRED');end if;
   v_cell:=pp.HU_CURRENT_CELL;v_status:=pp.HU_TYPE;
  elsif v_goods_kind='STOCK' then
   select count(*),min(CELL),min(STOCK_VERSION) into n,v_cell,v_stock_version from RRL_REMAINS where UID_POLETA=v_place and REMAIN>0;
   if n!=1 then raise_application_error(-20886,'TARE_STOCK_SINGLE_CURRENT_CELL_REQUIRED');end if;
   if kind='TARE_BOOK_CANCEL' then raise_application_error(-20886,'TARE_BOOK_EMPTY_PLACE_REQUIRED');end if;
   select count(*) into n from RRL_CASE_CARRIER_LOT where LOT_UID=v_place;
   if n!=0 then raise_application_error(-20886,'TARE_CASE_GOODS_USE_EXISTING_CASE_ROOT');end if;
   v_status:='STOCK_PALLET';
  else raise_application_error(-20886,'TARE_RETURNABLE_CURRENT_PLACE_REQUIRED');end if;
  select WARE_ID into v_ware from RRL_CELLS where CELL=v_cell;
  select LOAD_UNIT_CLASS into v_class from RRL_PALLET_TYPE where PALLET_TYPE_ID=v_type and ACTIVE=1;
  if(v_goods_kind='STOCK' and v_class!='PALLET')or(pp.HU_TYPE='PALLET' and v_class!='PALLET')or(pp.HU_TYPE='ROLL_CAGE' and v_class!='TROLLEY')then raise_application_error(-20886,'TARE_CONTAINER_PHYSICAL_TYPE_CONFLICT');end if;"""
assert old in s;s=s.replace(old,new,1)
s=s.replace("p_domain.put('balance_key'","p_domain.put('goods_kind',v_goods_kind);p_domain.put('article',v_article);p_domain.put('stock_version',v_stock_version);\n p_domain.put('balance_key'",1)
s=s.replace("p_policies:=f.to_clob;","if v.get_string('goods_kind')='STOCK' then RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('place_id'),v.get_string('article'),v.get_string('cell'),null);end if;\n p_policies:=f.to_clob;",1)
out[str(folder/"001_command.sql")]=s
out[str(folder/"apply.sql")]=Path("db/migrations/2026-10-10_ni063_fullpal_tare/apply.sql").read_text(encoding="utf-8-sig")
out[str(folder/"rollback.sql")]="@@../2026-10-08_stock_posting_core/413_before103_tare_book.sql\n"
print(json.dumps(out,ensure_ascii=True))
