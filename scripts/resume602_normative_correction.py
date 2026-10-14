exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_expenses import LogisticsExpenses
from app.modules.finance.infrastructure.normative_correction import confirmed_total
from app.oracle_gateway import OracleGateway
from app.modules.finance.contracts import LogisticsCostError
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import httpx
p=Path("tmp/context601.json")
prior=json.loads(p.read_text(encoding="utf-8"))
assert prior.get("retired")and not prior.get("requests")and not prior.get("done"),"No completed facts may be recreated"
retired_actor=prior["actor"]
original=json.loads(Path("tmp/context586.json").read_text(encoding="utf-8"));assert original["done"]
cost=original["winner"]["body"]["operation_id"];ware=original["warehouse"];trip=original["trip"]
tag=uuid4().hex[:8];actor="QNC601"+tag;group=actor.upper();secret=uuid4().hex;code="NORMCORR601."+tag
svc=LogisticsExpenses(OracleGateway())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own normative correction logistic',:grp,:ware,0,0)",
                      id=actor,secret=secret,grp=group,ware=ware);c.commit()
 saved=dict(retired_actors=[retired_actor],cost_operation_id=cost,warehouse=ware,trip=trip,actor=actor,group=group,article=code,tag=tag)
 p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
 try:
  with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=25)as api:
   r=api.post("/api/admin/rights/groups",json={"id":group,"name":"Own normative correction"});r.raise_for_status()
   for right in("transport_dispatch_view","edit_bill_tt","calc_tt_price"):
    r=api.post("/api/admin/rights/groups/"+group+"/rights",json={"right_name":right,"enabled":True});r.raise_for_status()
  svc.article(code,"Dev normative correction, not an actual business expense","TRIP",False,True,0,"admin")
  assert confirmed_total(q,cost)=="107.25"
  requests=[]
  for index in range(2):
   op="CORR601."+str(index)+":"+tag
   result=svc.report(op,ware,code,"TRIP",trip,"-107.25","GEL","2026-10-12","DEV601:"+tag,"Synthetic dev competing full-credit case",actor,None,"107.25",cost)
   assert result["amount"]=="-107.25"and result["cost_correction_of_operation_id"]==cost
   assert svc.report(op,ware,code,"TRIP",trip,"-107.25","GEL","2026-10-12","DEV601:"+tag,"Synthetic dev competing full-credit case",actor,None,"107.25",cost)==result
   logist=svc.decide(op+".LOGIST",op,"LOGIST","APPROVE","WEIGHT","LOGIST601:"+tag,"Own source proof, quantity unchanged",actor)
   requests.append(dict(operation=op+".FINANCE",expense=op))
  saved["requests"]=requests;p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
  def decide(body):
   try:return dict(result=svc.decide(body["operation"],body["expense"],"FINANCE","APPROVE","WEIGHT","FIN601:"+tag,"Own independent finance decision","admin"),body=body)
   except LogisticsCostError as exc:return dict(error=exc.code,message=str(exc),body=body)
  with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(decide,requests))
  winners=[r for r in results if "result"in r];losers=[r for r in results if "error"in r]
  assert len(winners)==len(losers)==1,results
  assert "NORMATIVE_CORRECTION_CURRENT_TOTAL"in losers[0]["message"]
  assert confirmed_total(q,cost)=="0"
  winner=winners[0];assert decide(winner["body"])["result"]==winner["result"]
  q.execute("select json_value(RESULT_JSON,'$.total')from RRL_LOGISTICS_COST_RUN where OPERATION_ID=:op",op=cost);assert q.fetchone()[0]=="107.25"
  q.execute("select count(*)from RRL_LOGISTICS_EXP_DECISION f join RRL_LOGISTICS_EXPENSE e on e.OPERATION_ID=f.EXPENSE_OPERATION_ID where e.COST_CORRECTION_OF_OP=:cost and f.PHASE='FINANCE'and f.OUTCOME='APPROVE'",cost=cost);assert q.fetchone()[0]==1
  q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where json_value(PAYLOAD_JSON,'$.cost_correction_of_operation_id')=:cost",cost=cost);assert q.fetchone()[0]==1
  saved.update(results=results,confirmed_total="0",done=True);p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
  print("PASS601 existing signed expense reports/independent LOGIST and FINANCE reused: two full credits compete, one approved/one stale refusal, original107.25 immutable/current total0/outbox1/no stock or carrier price change.")
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:actor",actor=actor);c.commit();saved["retired"]=True;p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
