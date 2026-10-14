import sys
from pathlib import Path
from uuid import uuid4
from decimal import Decimal
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QPC"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def api(client,path,body,status=200):
 r=client.post(base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1500]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();ware=2378876;p="/api/finance/logistics-expenses"
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own decimal precision observer',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api(admin,"/api/admin/rights/groups",{"id":group,"name":"Own exact decimal proof"})
 for right in ["transport_dispatch_view","edit_bill_tt","calc_tt_price"]:
  api(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own exact decimal source"})
 try:
  amount="12345678901234567.89"
  report={"operation_id":"EX.PRECISION:"+tag,"warehouse_id":ware,"article_code":"EX.QA:80B1FC8567","object_kind":"TRIP","object_id":33514,"amount":amount,"currency":"GEL","expense_date":"2026-10-10","document_reference":"DEV.PRECISION:"+tag,"reason":"Synthetic dev-only decimal boundary; no real money"}
  assert api(user,p+"/report",report)["amount"]==amount
  api(user,p+"/report",{**report,"operation_id":"EX.DUP.DOC:"+tag},409)
  decision={"operation_id":"EX.PREC.LOGIST:"+tag,"expense_operation_id":report["operation_id"],"phase":"LOGIST","outcome":"APPROVE","distribution_basis":"WEIGHT","decision_reference":"LOGIST:"+tag,"reason":"Synthetic dev precision source"}
  api(user,p+"/decide",decision)
  api(admin,p+"/decide",{**decision,"operation_id":"EX.PREC.FIN:"+tag,"phase":"FINANCE"})
  body={"operation_id":"EX.PREC.ALLOC:"+tag,"expense_operation_id":report["operation_id"]}
  result=api(admin,"/api/finance/expense-allocation",body)
  assert result["amount"]==amount and sum(Decimal(x["amount"])for x in result["lines"])==Decimal(amount)
  assert api(admin,"/api/finance/expense-allocation",body)==result
  q.execute("select to_char(sum(AMOUNT),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')from RRL_LOGISTICS_EXP_ALLOC_LINE where OPERATION_ID=:op",op=body["operation_id"])
  assert Decimal(q.fetchone()[0])==Decimal(amount)
  print("PASS113 exact Oracle Decimal12345678901234567.89 through original report/two approvals/source weight/allocation/sum/replay; duplicate document new ID denied; synthetic dev only; tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
