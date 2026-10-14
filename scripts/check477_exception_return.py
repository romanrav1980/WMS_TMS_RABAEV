exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
from app.modules.platform.public import read_oracle_json
ctx=json.loads(Path("tmp/context383.json").read_text(encoding="utf-8"));receipt=ctx["body"]["operation_id"]
base="http://127.0.0.1:8088/api/delivery/store-returns"
with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
 r=client.get(base+"/"+receipt);assert r.status_code==200,r.text;source=r.json()
 assert len(source["units"])==5 and {u["return_basis"]for u in source["units"]}=={"ACCEPTED","REFUSED","DAMAGED"},source
 line=source["lines"][0];assert line["accepted_quantity"]=="3"and line["refused_available"]=="1"and line["damaged_available"]=="1",line
 selected={kind:[u["key"]for u in source["units"]if u["return_basis"]==kind]for kind in ["REFUSED","DAMAGED"]}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def native(basis,qty,keys,op,destination):
  request=dict(contract_version=2,operation_id=op,command_type="STORE_RETURN_APPROVE",actor="admin",source=dict(receipt_operation_id=receipt,line_no=line["line_no"]),lines=[],units=[],metadata=dict(return_basis=basis,quantity=qty,unit_keys=keys,disposition=destination,reason="Delivery exception physical return",decision_reference="DEV477:unaccepted-cargo",complete_good_box=False))
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(request),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   return read_oracle_json(out.getvalue())
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 for basis in ["REFUSED","DAMAGED"]:
  result=native(basis,"1",selected[basis],"EXRET477.TRIAL:"+basis,"SUPPLIER"if basis=="REFUSED"else"DISPOSAL")
  assert result["return_basis"]==basis and result["customer_accepted_quantity_changed"]is False,result
  q.execute("select ACCEPTED_BASE_QTY,REFUSED_BASE_QTY,DAMAGED_BASE_QTY from RRL_STORE_RECEIPT_LINE where OPERATION_ID=:op and LINE_NO=:line",op=receipt,line=line["line_no"]);assert q.fetchone()==(3,1,1)
  c.rollback()
 for basis,qty,keys,disposition in [("REFUSED","2",selected["REFUSED"],"SUPPLIER"),("REFUSED","1",selected["DAMAGED"],"SUPPLIER"),("MISSING","1",selected["REFUSED"],"SUPPLIER"),("DAMAGED","1",selected["DAMAGED"],"REUSE")]:
  try:native(basis,qty,keys,"EXRET477.BAD:"+basis+qty+disposition+keys[0][-5:],disposition)
  except oracledb.DatabaseError as e:assert e.args[0].code==20886,str(e)
  else:raise AssertionError("Wrong disposition/quantity/keys admitted")
  finally:c.rollback()
 q.execute("select count(*)from RRL_STORE_RETURN_APPROVAL where RECEIPT_OPERATION_ID=:op",op=receipt);assert q.fetchone()[0]==0
 print("PASS477 source5 eligible keys/3Accepted+1Refused+1Damaged; native each1 approval late rollback; missing/excess/wrong disposition keys/reuse rejected; buyerAccepted3 unchanged")
print(json.dumps({"receipt":receipt,"source":source,"selected":selected}))
