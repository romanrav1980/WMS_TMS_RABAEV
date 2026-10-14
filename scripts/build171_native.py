import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];f=r/"db/migrations/2026-10-11_ni033_line_demand";s=(f/"000_before_pool.sql").read_text(encoding="utf-8")
out={}
needle=" function snapshot_json(p_ware number,p_article varchar2) return clob;"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n function line_snapshot_json(p_line number) return clob;",1)
start=s.index("   if o.UNIT_CODE is null")
end=s.index("   x.put('dispatch_order'",start)
calculation=s[start:end]
calculation=calculation.replace("qty:=greatest(0,qty-hard_qty-greatest(0,picked_qty-picked_hard));","requested:=qty;qty:=greatest(0,qty-hard_qty-greatest(0,picked_qty-picked_hard));")
function=""" function line_snapshot_json(p_line number)return clob is
  o RRL_CUSTOMER_ORDER_ROW%rowtype;h RRL_CUSTOMER_ORDER%rowtype;
  base varchar2(20);p_article varchar2(160);qty number;requested number;hard_qty number;picked_qty number;picked_hard number;
  num number;den number;scale number;conversion number;x json_object_t;
  v_row_status varchar2(40);v_order_status varchar2(40);v_customer number;
 begin
  if p_line is null or p_line<1 or p_line!=trunc(p_line)then raise_application_error(-20881,'POOL_LINE_IDENTITY_REQUIRED');end if;
  select *into o from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=p_line;
  select *into h from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID;
  p_article:=o.ARTICUL;v_row_status:=o.STATUS;v_order_status:=h.STATUS;v_customer:=h.CUSTOMER_ID;
  select BASE_UOM into base from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1
   order by POLICY_VERSION desc fetch first 1 row only;
"""+calculation.replace("o.ROW_STATUS","v_row_status").replace("o.ORDER_STATUS","v_order_status").replace("o.CUSTOMER_ID","v_customer")+"""
  x.put('warehouse',nvl(o.WARE_ID,h.WARE_ID));x.put('article',p_article);x.put('unit',base);
  x.put('requested_base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(requested));
  x.put('quantity_semantics','UNALLOCATED_BASE_NOT_SHIPPED_PROOF');
  x.put('open',v_row_status in('OPEN','PLANNED_FULL','PLANNED_PARTIAL','NO_STOCK')and
    v_order_status in('IMPORTED','OPEN','PLANNED_FULL','PLANNED_PARTIAL','NO_STOCK')and o.ORDER_QTY>0);
  return x.to_clob;
 exception when no_data_found then raise_application_error(-20868,'POOL_LINE_OR_UOM_NOT_FOUND');end;
"""
replacement="""   x:=json_object_t.parse(line_snapshot_json(o.CUSTOMER_ORDER_ROW_ID));
   x.remove('warehouse');x.remove('article');x.remove('unit');x.remove('requested_base_quantity');x.remove('quantity_semantics');x.remove('open');
"""
s=s[:start]+replacement+s[end:]
pos=s.index(" function snapshot_json(",s.index("create or replace package body"))
s=s[:pos]+function+s[pos:]
out[str(f.relative_to(r)/"001_pool.sql")]=s
out[str(f.relative_to(r)/"apply.sql")]="-- MIGRATION_ID:2026-10-11-171-existing-line-demand\n@@001_pool.sql\n"
out[str(f.relative_to(r)/"rollback.sql")]="@@000_before_pool.sql\n-- Source rollback only, no domain/stock history changes.\n"
out[str(f.relative_to(r)/"verify.sql")]="select OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_POOL_READ';\nselect LINE,TEXT from USER_ERRORS where NAME='RRL_STOCK_POOL_READ';\n"
print(json.dumps(out))
