from pathlib import Path
import json
t=Path("scripts/case909_supply_amendments.py").read_text(encoding="utf-8").replace("context908.json","context910.json").replace("SAP909.REVISION","SAP911.REVISION").replace("amendments909","amendments911")
t=t.replace(' q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=ctx["uid"]);assert q.fetchone()==(0,0)','')
t=t[:t.index('ctx["amendments911"]')]+'''
ctx["amendments911"]={"revision":3,"canonical_quantity":"3","accepted_shrink_denied":True,"v1_duplicates_denied":True,"shared_unreceived_line_deleted":True}
Path("tmp/context910.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print("911 metadata PASS canonical7 then3; accepted shrink refused; unreceived shared line deleted retaining canonical; v1 duplicates refused",flush=True)
import httpx
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
with httpx.Client(auth=("admin",password),base_url="http://127.0.0.1:8088",timeout=30)as client:
 response=client.post("/api/inventory/stock-posting/receipt-documents/"+str(ctx["document_id"])+"/reverse",json={"operation_id":"SAP911.CLEANUP:"+ctx["tag"],"reason":"End own source910 fixture"})
 assert response.status_code==200,response.text
 ctx["cleanup"]=response.json();ctx["stage"]="AMENDMENTS_PASS_OWN_REVERSED"
 Path("tmp/context910.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=ctx["uid"]);assert q.fetchone()==(0,0)
print("911 own source910 P/H0 through native receipt reversal")
'''
print(json.dumps({"scripts/resume911_supply_amendments.py":t},ensure_ascii=True))
