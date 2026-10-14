import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];f=r/"db/migrations/2026-10-11_ni032_remaining_plan";s=(f/"000_before_picking.sql").read_text(encoding="utf-8");out={}
needle="    v_release varchar2(20);v_requested_line_qty number;v_uom varchar2(20);v_version number;v_num number;v_den number;v_scale number;"
assert needle in s
s=s.replace(needle,needle+"v_demand json_object_t;v_soft number;")
needle="    select STATE into v_release from RRL_STOCK_RELEASE where RELEASE_ID=1;"
assert s.count(needle)==1
s=s.replace(needle,needle+"\n    if v_release='ACTIVE'then RRL_PICK_PLAN_ADMISSION.begin_plan(p_customer_order_id,p_created_by);end if;",1)
needle="       v_requested_line_qty:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(l.ORDER_QTY),v_num,v_den,v_scale);"
assert s.count(needle)==1
s=s.replace(needle,"""       v_demand:=json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(l.CUSTOMER_ORDER_ROW_ID));
       if not v_demand.get_boolean('open')then continue;end if;
       v_requested_line_qty:=to_number(v_demand.get_string('quantity'),'TM9','NLS_NUMERIC_CHARACTERS=''.,''');
       select nvl(sum(pr.RESERVED_QTY),0)into v_soft from RRL_PICK_RESERVATION pr
        join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pr.PICK_PLAN_LINE_ID join RRL_PICK_PLAN pp on pp.PICK_PLAN_ID=pl.PICK_PLAN_ID
        where pl.CUSTOMER_ORDER_ROW_ID=l.CUSTOMER_ORDER_ROW_ID and pr.RESERVATION_STATUS='ACTIVE'and pr.RESERVATION_LEVEL='SOFT'
         and pp.STATUS in('DRAFT','PLANNED_FULL','PLANNED_PARTIAL');
       v_requested_line_qty:=greatest(0,v_requested_line_qty-v_soft);
       if v_requested_line_qty=0 then continue;end if;""")
needle="        exit when v_remaining <= 0;"
assert s.count(needle)==1
s=s.replace(needle,needle+"""
        if v_release='ACTIVE'then
         begin RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',c.UID_POLETA));
         exception when others then if sqlcode=-20850 then raise_application_error(-20890,'PICK_PLAN_SOURCE_CHANGED_RETRY');else raise;end if;end;
        end if;""")
needle="    if v_requested_total = 0 then\n      v_status := 'NO_STOCK';"
assert s.count(needle)==1
s=s.replace(needle,"""    if v_release='ACTIVE'and v_requested_total=0 then raise_application_error(-20886,'PICK_ORDER_DEMAND_ALREADY_PLANNED_OR_SECURED');end if;
"""+needle)
needle="    return v_pick_plan_id;\n  end create_plan;"
assert s.count(needle)==1
s=s.replace(needle,"""    if v_release='ACTIVE'then RRL_PICK_PLAN_ADMISSION.end_plan;end if;
    return v_pick_plan_id;
  exception when others then
    if v_release='ACTIVE'then RRL_PICK_PLAN_ADMISSION.end_plan;end if;
    raise;
  end create_plan;""")
out[str(f.relative_to(r)/"002_picking_contract.sql")]=s
out[str(f.relative_to(r)/"002_picking_body.sql")]=s[s.lower().index("create or replace package body"):]
a=(f/"001_admission.sql").read_text(encoding="utf-8").replace("anchor(r,50,'STOCK',stock.UID_POLETA,stock.CELL)","anchor(r,50,'STOCK',stock.UID_POLETA)")
out[str(f.relative_to(r)/"001_admission.sql")]=a
out[str(f.relative_to(r)/"apply.sql")]="-- MIGRATION_ID:2026-10-11-174-remaining-pick-plan\n@@001_admission.sql\n@@002_picking_body.sql\n"
out[str(f.relative_to(r)/"rollback.sql")]="@@000_before_picking.sql\n-- Keep additive helper until no callers; no data/history/stock deletion.\n"
out[str(f.relative_to(r)/"verify.sql")]="select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_PICK_PLAN_ADMISSION','RRL_PICKING_API');\nselect NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_PICK_PLAN_ADMISSION','RRL_PICKING_API');\n"
print(json.dumps(out))
