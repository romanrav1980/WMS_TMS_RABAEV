exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.public import build_stock_posting_service
from app.oracle_gateway import OracleGateway
ctx=json.loads(Path("tmp/context314_received.json").read_text(encoding="utf-8"));source=ctx["source"];p=Path("tmp/context318.json")
service=Interwarehouse(OracleGateway(),build_stock_posting_service());op="IW318.CUSTODY:"+source["tag"]
result=service.release_custody(op,ctx["operation_id"],"admin");assert result["pallet_identifier"]==source["physical_root"]and result["stock_changed"]is False,result
assert service.release_custody(op,ctx["operation_id"],"admin")==result
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select STATUS,CUSTODY_RELEASE_OPERATION_ID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=source["source_load"]);assert q.fetchone()==("DEPARTED",op)
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot_id",lot_id=source["lot"]);assert q.fetchone()==(3,0)
 q.execute("select count(*)from RRL_INTERWARE_CUSTODY_PROOF where RECEIPT_OPERATION_ID=:receipt_id",receipt_id=ctx["operation_id"]);assert q.fetchone()[0]==1
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
p.write_text(json.dumps(dict(source=source,receipt_operation_id=ctx["operation_id"],result=result),indent=2),encoding="utf-8")
print("PASS318 actual topHU custodyrelease/exactrepeat/oldDEPARTED preserved/stockleafP3H0 unchanged/one proof/protected20-20")
