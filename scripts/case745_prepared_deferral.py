exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.st_deferral import StDeferral
from app.modules.platform.public import read_oracle_json
p=Path("tmp/context744.json");data=json.loads(p.read_text(encoding="utf-8"));service=StDeferral(OracleGateway())
ctx=service.context(data["st_uid"],"admin");assert ctx["physical_preparation"]["state"]=="PREPARED_WHOLE_STOCK"
body={"st_number":data["st_uid"],"target_trip_id":data["ids"][-1],"expected_version":ctx["version"],"source_hash":ctx["source_hash"],"reason":"Whole completed flat pallet postponed to next planned day; physical movement is separate","reference":"DEV745:"+data["tag"]}
op="ST745:"+data["tag"];data["defer_body"]=body;data["defer_operation"]=op;p.write_text(json.dumps(data,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_ST_DEFER_API.apply_decision",[op,"admin",json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=True),out])
 trial=read_oracle_json(out.getvalue());assert trial["physical_preparation"]["physical_move_required"]and not trial["stock_changed"]
 c.rollback();q.execute("select TRANSTASK_ID from RRL_SBORKA_PALLETS where ST_NUMBER=:st",st=data["st_uid"]);assert q.fetchone()[0]==data["ids"][-2]
 q.execute("select count(*)from RRL_ST_DEFER_DECISION where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
result=service.defer(op,body,"admin");data["defer_result"]=result;data["stage"]="DEFERRED_PREPARED";p.write_text(json.dumps(data,indent=2),encoding="utf-8")
assert service.defer(op,body,"admin")==result
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=data["lot"],cell=data["dst"]);assert q.fetchone()==(3,3)
 q.execute("select STATUS,FACT_QTY,PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:ff",ff=data["ids"][9]);assert q.fetchone()==("PICKED",3,data["lot"])
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3),round(buffer_gets/nullif(executions,0),1)from V$SQL where sql_text like '%LOT_FACT_QTY%'and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL",q.fetchall())
print("PASS745 original source688 UID47 picked/bound3 then original native deferral; rollback/replay/P3H3/FF PICKED3/original source qty/no stock events/P20H20 unchanged; physical waiting move remains separate")
