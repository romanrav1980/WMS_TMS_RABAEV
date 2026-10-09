"""Preserve legacy supplier-return source; never consume ordinary pick stock instead."""
import json
from pathlib import Path
p=Path("db/migrations/2026-10-08_stock_posting_core/068_shipping.sql");s=p.read_text(encoding="utf-8")
s=s.replace("v_ware number;v_cell varchar2(60);","v_ware number;v_cell varchar2(60);v_return_supplier varchar2(255);",1)
s=s.replace("select ID,WARE_ID into v_id,v_ware from RRL_SBORKA_PALLETS where PALLET_UID=v_uid;","select ID,WARE_ID,RETURN_SUPPLIER_ID into v_id,v_ware,v_return_supplier from RRL_SBORKA_PALLETS where PALLET_UID=v_uid;",1)
s=s.replace("   select CELL into v_cell from RRL_ARTICULS where ACTICUL=v_article;","   if v_return_supplier is not null then\n    v_cell:='RETURNS';\n    RRL_STOCK_PLAN_HELPER.fence(f,'CELL',v_cell);\n    declare v_return_ware number;begin\n     select WARE_ID into v_return_ware from RRL_CELLS where CELL=v_cell;\n     if v_return_ware is null or v_return_ware!=v_ware then raise_application_error(-20886,'SUPPLIER_RETURN_LOCATION_REQUIRED');end if;\n    exception when no_data_found then raise_application_error(-20886,'SUPPLIER_RETURN_LOCATION_REQUIRED');end;\n   else select CELL into v_cell from RRL_ARTICULS where ACTICUL=v_article;end if;",1)
s=s.replace("  v.put('customer_order_id',v_customer_order);","  v.put('return_supplier_id',v_return_supplier);v.put('customer_order_id',v_customer_order);",1)
s=s.replace("v_remaining number;sr RRL_STOCK_RESERVATION%rowtype;","v_remaining number;v_return_supplier varchar2(255);sr RRL_STOCK_RESERVATION%rowtype;",1)
s=s.replace("else select CONDITION into v_condition from RRL_SBORKA_PALLETS where ID=v_id for update;end if;","else select CONDITION,RETURN_SUPPLIER_ID into v_condition,v_return_supplier from RRL_SBORKA_PALLETS where ID=v_id for update;\n   if nvl(v_return_supplier,chr(1))!=nvl(v.get_string('return_supplier_id'),chr(1)) then raise_application_error(-20890,'CLOSURE_CHANGED: supplier return');end if;end if;",1)
print(json.dumps({str(p):s},ensure_ascii=True))
