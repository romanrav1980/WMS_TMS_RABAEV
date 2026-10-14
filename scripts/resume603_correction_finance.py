exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_expenses import LogisticsExpenses
from app.modules.finance.infrastructure.normative_correction import confirmed_total
from app.modules.finance.contracts import LogisticsCostError
from app.oracle_gateway import OracleGateway
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
p=Path("tmp/context601.json");d=json.loads(p.read_text(encoding="utf-8"));assert d["retired"]and not d.get("done")
tag=d["tag"];cost=d["cost_operation_id"];ware=d["warehouse"];trip=d["trip"];code=d["article"]
actor="QNC603"+uuid4().hex[:8];svc=LogisticsExpenses(OracleGateway())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();first="CORR601.0:"+tag;second="CORR601.1:"+tag
 q.execute("select count(*)from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id and COST_CORRECTION_OF_OP=:cost",id=first,cost=cost);assert q.fetchone()[0]==1
 q.execute("select count(*)from RRL_LOGISTICS_EXP_DECISION where EXPENSE_OPERATION_ID=:id and PHASE='LOGIST'and OUTCOME='APPROVE'",id=first);assert q.fetchone()[0]==1
 q.execute("select count(*)from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id",id=second);assert q.fetchone()[0]==0
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own second normative correction logistic',:grp,:ware,0,0)",
                      id=actor,secret=uuid4().hex,grp=d["group"],ware=ware);c.commit()
 d["retired_actors"]=d.get("retired_actors",[])+[d["actor"]];d["second_actor"]=actor;p.write_text(json.dumps(d,indent=2),encoding="utf-8")
 try:
  result=svc.report(second,ware,code,"TRIP",trip,"-107.25","GEL","2026-10-12","DEV601:"+tag+".1","Synthetic dev competing full-credit case",actor,None,"107.25",cost)
  assert result["amount"]=="-107.25"
  svc.decide(second+".LOGIST",second,"LOGIST","APPROVE","WEIGHT","LOGIST603:"+tag,"Own distinct documentary credit",actor)
  requests=[dict(operation=op+".FINANCE",expense=op)for op in(first,second)]
  d["requests"]=requests;p.write_text(json.dumps(d,indent=2),encoding="utf-8")
  def decide(body):
   try:return dict(result=svc.decide(body["operation"],body["expense"],"FINANCE","APPROVE","WEIGHT","FIN603:"+tag,"Own independent finance decision","admin"),body=body)
   except LogisticsCostError as exc:return dict(error=exc.code,message=str(exc),body=body)
  with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(decide,requests))
  winners=[r for r in results if "result"in r];losers=[r for r in results if "error"in r]
  assert len(winners)==len(losers)==1,results
  assert "NORMATIVE_CORRECTION_CURRENT_TOTAL"in losers[0]["message"],results
  assert confirmed_total(q,cost)=="0"
  assert decide(winners[0]["body"])["result"]==winners[0]["result"]
  q.execute("select json_value(RESULT_JSON,'$.total')from RRL_LOGISTICS_COST_RUN where OPERATION_ID=:op",op=cost);assert q.fetchone()[0]=="107.25"
  q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where json_value(PAYLOAD_JSON,'$.cost_correction_of_operation_id')=:cost",cost=cost);assert q.fetchone()[0]==1
  d.update(results=results,confirmed_total="0",done=True);p.write_text(json.dumps(d,indent=2),encoding="utf-8")
  print("PASS603 retained first credit/original independent approval + distinct second documentary credit: concurrent finance one winner/one stale rejection; original107.25 immutable, confirmed total0, correction outbox1. Old actors stay retired, no source recreation.")
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:actor",actor=actor);c.commit();d["second_actor_retired"]=True;p.write_text(json.dumps(d,indent=2),encoding="utf-8")
