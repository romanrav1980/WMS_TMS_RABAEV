exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.services.picking_service import PickingService
from app.modules.fulfillment.public import build_fulfillment_read_service
plan=PickingService().get_plan(2187)
result={"plan_id":plan["pick_plan_id"],"status":plan["status"],"order":plan["customer_order_id"],"total_order_qty":plan.get("total_order_qty"),"total_planned_qty":plan.get("total_planned_qty"),"total_shortage_qty":plan.get("total_shortage_qty"),"lines":len(plan.get("lines",[])),"tasks":len(plan.get("tasks",[]))}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=9807");result["stock"]=q.fetchone();assert result["stock"]==(0,0)
 q.execute("select count(*)from RRL_PICK_PLAN where CUSTOMER_ORDER_ID=2135 and STATUS!='CANCELLED'");result["active_plan_count"]=q.fetchone()[0];assert result["active_plan_count"]==1
 print(json.dumps(result));Path("tmp/plan1231.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
