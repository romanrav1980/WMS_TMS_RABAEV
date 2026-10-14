exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse_recovery_st import prepare_recovery_st
from app.modules.transport.public import create_existing_trip,update_existing_trip,assign_sts
from app.oracle_gateway import OracleGateway
from datetime import date
gw=OracleGateway()
for number in [291,292]:
 ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"));placed=json.loads(Path("tmp/context301_"+str(number)+".json").read_text(encoding="utf-8"))
 target=json.loads(Path("tmp/context296_"+str(number)+".json").read_text(encoding="utf-8"))
 p=Path("tmp/context302_"+str(number)+".json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {}
 if "trip_id"not in saved:
  saved["trip_id"]=create_existing_trip(gw,"15",date(2026,10,12),"admin");p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
 trip=saved["trip_id"]
 if "prepared"not in saved:
  with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
   q=c.cursor();q.execute("select VODITEL_ID from RRL_TRANSPORT_TASK where ID=:trip_id",trip_id=ctx["target_trip"]);driver=q.fetchone()[0]
  update_existing_trip(gw,trip,dict(transport=target["target_vehicle_number"],transtype="15",dock=ctx["outbound"],voditel_id=driver),"admin")
  op="IW302.ST:"+str(number)+":"+ctx["tag"];body=dict(operation=op,recovery_id=placed["recovery_operation_id"],trip=trip,reason="Доставка найденного остатка исходному покупателю",reference="DEV302:corrective2",actor="admin")
  result=prepare_recovery_st(gw,**body);saved.update(prepared=result,prepare_body=body);p.write_text(json.dumps(saved,ensure_ascii=False,indent=2),encoding="utf-8")
  assign_sts(gw,trip,[result["st_number"]],"admin");saved["assigned"]=True;p.write_text(json.dumps(saved,ensure_ascii=False,indent=2),encoding="utf-8")
 assert prepare_recovery_st(gw,**saved["prepare_body"])==saved["prepared"]
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell_code",lot_id=saved["prepared"]["pallet_identifier"],cell_code=ctx["outbound"]);assert q.fetchone()==(2,0)
  q.execute("select count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:st_id",st_id=saved["prepared"]["st_id"]);assert q.fetchone()==(0,)
print("PASS302 originalST constructor/existingtripassignment wholefound2/oneimmutablebinding/replay/no duplicateFF/P2 unchanged")
