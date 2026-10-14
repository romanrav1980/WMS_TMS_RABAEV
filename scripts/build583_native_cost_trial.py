from pathlib import Path
v=Path("scripts/case578_transport_preview_trial.py").read_text(encoding="utf-8")
v=v.replace("from app.modules.finance.infrastructure.transport_cost_preview import preview_transport_cost",'''from app.modules.platform.public import read_oracle_json
def preview_transport_cost(q,trip,ware,price,actor):
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_TRANSPORT_COST_API.preview",[trip,ware,price,actor,out])
 return read_oracle_json(out.getvalue())''')
v=v.replace("578","583")
anchor='  assert blocked["missing"]==[]'
v=v.replace(anchor,anchor+'''
  request=dict(operation_id="COST583.TRIAL:"+ctx["tag"],trip_id=trip,warehouse_id=ware,source_price_id=price,currency="GEL")
  q.callproc("RRL_TRANSPORT_COST_API.conduct",[json.dumps(request),"admin",out])
  recognized=read_oracle_json(out.getvalue());assert recognized["cost_posted"]and recognized["total"]=="107.25"
  q.callproc("RRL_TRANSPORT_COST_API.conduct",[json.dumps(request),"admin",out]);assert read_oracle_json(out.getvalue())==recognized
  try:q.callproc("RRL_TRANSPORT_COST_API.conduct",[json.dumps({**request,"currency":"USD"}),"admin",out]);raise AssertionError("Changed payload accepted")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20867
  q.execute("select count(*),sum(AMOUNT)from RRL_TRANSPORT_COST_DETAIL where OPERATION_ID=:op",op=request["operation_id"])
  assert q.fetchone()==(3,107.25)
  q.execute("select count(*)from RRL_TRANSPORT_COST_CLAIM where OPERATION_ID=:op",op=request["operation_id"]);assert q.fetchone()[0]==1
  q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where json_value(PAYLOAD_JSON,'$.operation_id')=:op",op=request["operation_id"]);assert q.fetchone()[0]==1
''')
anchor=' q.execute("select count(*)from RRL_TRANSPORT_PRICE where ID=:id",id=price);assert q.fetchone()[0]==0'
v=v.replace(anchor,anchor+'''
 q.execute("select count(*)from RRL_LOGISTICS_COST_RUN where OPERATION_ID=:op",op="COST583.TRIAL:"+ctx["tag"]);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_TRANSPORT_COST_CLAIM where OPERATION_ID=:op",op="COST583.TRIAL:"+ctx["tag"]);assert q.fetchone()[0]==0
 q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where json_value(PAYLOAD_JSON,'$.operation_id')=:op",op="COST583.TRIAL:"+ctx["tag"]);assert q.fetchone()[0]==0
''')
v=v.replace("all synthetic tariff/history rolled back, no money or stock posting.","same native preview/conduct107.25, exact repeat one header/claim/3 lines/outbox1, changed body refused; outer rollback removes all monetary facts/tariff/history, stock unchanged.")
Path("scripts/case583_native_cost_trial.py").write_text(v,encoding="utf-8")
print("583 native bounded trial authored.")
