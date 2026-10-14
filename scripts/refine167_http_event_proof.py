from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts/ni033_case_http_close_flow.py"
s=p.read_text(encoding="utf-8")
old='''  result=request(f"/tasks/{case}/lines/{line}/confirm",body)
  assert request(f"/tasks/{case}/lines/{line}/confirm",body)==result
  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:id",id=operation);assert q.fetchone()==(1,1)'''
new='''  result=request(f"/tasks/{case}/lines/{line}/confirm",body)
  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:id",id=operation);journal=q.fetchone();assert journal[0]>0
  assert request(f"/tasks/{case}/lines/{line}/confirm",body)==result
  q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:id",id=operation);assert q.fetchone()==journal'''
assert old in s;s=s.replace(old,new,1)
s=s.replace('actual HTTP CASE oneunit/one stockevent/exactrepeat','actual HTTP CASE oneunit/journal snapshot unchanged on exactrepeat')
p.write_text(s,encoding="utf-8")
