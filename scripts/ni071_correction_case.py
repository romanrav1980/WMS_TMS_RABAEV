import sys
from pathlib import Path
from uuid import uuid4
from decimal import Decimal
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QXC"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body,status=200):
 r=client.post(base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=15000;q=c.cursor();ware=2378876;p="/api/finance/logistics-expenses";root="EX.PRECISION:f57025b124";amount="12345678901234567.89"
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own signed correction observer',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own late correction"})
 for right in ["transport_dispatch_view","edit_bill_tt","calc_tt_price"]:
  api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own linked expense correction"})
 try:
  q.execute("select count(*)from RRL_EVENTS");goods=q.fetchone()[0]
  report={"operation_id":"EX.CORRECT:"+tag,"warehouse_id":ware,"article_code":"EX.QA:80B1FC8567","object_kind":"TRIP","object_id":33514,"amount":"-"+amount,"currency":"GEL","expense_date":"2026-10-10","document_reference":"DEV.CREDIT:"+tag,"reason":"Reverse synthetic large precision fixture through immutable linked credit","correction_of_operation_id":root,"expected_confirmed_total":amount}
  saved=api(user,p+"/report",report);assert saved["amount"]=="-"+amount and api(user,p+"/report",report)==saved
  alternate={**report,"operation_id":"EX.CORRECT.STALE:"+tag,"document_reference":"DEV.STALE:"+tag}
  api(user,p+"/report",alternate)
  decision={"operation_id":"EX.CORR.LOGIST:"+tag,"expense_operation_id":report["operation_id"],"phase":"LOGIST","outcome":"APPROVE","distribution_basis":"WEIGHT","decision_reference":"LOGIST:"+tag,"reason":"Linked original agreed source"}
  api(user,p+"/decide",{**decision,"operation_id":"EX.BAD.BASIS:"+tag,"distribution_basis":"BASE_QUANTITY"},409)
  api(user,p+"/decide",decision)
  stale_decision={**decision,"operation_id":"EX.STALE.LOGIST:"+tag,"expense_operation_id":alternate["operation_id"]}
  api(user,p+"/decide",stale_decision)
  finance={**decision,"operation_id":"EX.CORR.FIN:"+tag,"phase":"FINANCE"};api(admin,p+"/decide",finance)
  api(admin,p+"/decide",{**stale_decision,"operation_id":"EX.STALE.FIN:"+tag,"phase":"FINANCE"},409)
  api(admin,p+"/decide",{**stale_decision,"operation_id":"EX.STALE.REJECT:"+tag,"phase":"FINANCE","outcome":"REJECT"})
  body={"operation_id":"EX.CORR.ALLOC:"+tag,"expense_operation_id":report["operation_id"]}
  allocated=api(admin,"/api/finance/expense-allocation",body)
  assert allocated["amount"]=="-"+amount and sum(Decimal(x["amount"])for x in allocated["lines"])==-Decimal(amount)
  assert api(admin,"/api/finance/expense-allocation",body)==allocated
  q.execute("""select to_char(e.AMOUNT+nvl((select sum(c.AMOUNT*c.ADJUSTMENT_SIGN)from RRL_LOGISTICS_EXPENSE c join RRL_LOGISTICS_EXP_DECISION f on f.EXPENSE_OPERATION_ID=c.OPERATION_ID and f.PHASE='FINANCE' and f.OUTCOME='APPROVE'where c.CORRECTION_OF_OP=e.OPERATION_ID),0),'TM9')from RRL_LOGISTICS_EXPENSE e where e.OPERATION_ID=:id""",id=root)
  assert Decimal(q.fetchone()[0])==0
  api(user,p+"/report",{**report,"operation_id":"EX.OVER.CREDIT:"+tag,"document_reference":"DEV.OVER:"+tag,"amount":"-0.01","expected_confirmed_total":"0"},409)
  q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()[0]==goods
  print("PASS114 linked late credit exact original synthetic magnitude/dual decisions/original basis, two pending credits second final stale denied and rejected, signed allocation/replay/confirmed net0/overcredit denied/history retained/no goods; tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%CORRECTION_OF_OP%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 3 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
