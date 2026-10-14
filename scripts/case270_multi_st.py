exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.plan_application import assign_validated_sts
from app.modules.platform.public import read_oracle_json
from datetime import datetime
from uuid import uuid4
import httpx
p=Path("tmp/context270.json");assert not p.exists(),"Reuse owned context270 instead of duplicating planning rows"
tag=uuid4().hex[:10];number="M270:"+tag;trip=33564;ware=9807;uid_prefix="MULTI270.P:"+tag
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select count(*)from RRL_SBORKA_PALLETS where TRANSTASK_ID=:trip_id",trip_id=trip);assert q.fetchone()==(0,),"Existing owned empty259 trip no longer empty"
 q.execute("select ADDR from RRL_ADDR where ADDR is not null order by ADDR fetch first 1 rows only");address=q.fetchone()[0]
 q.execute("select NAME,BARCODE_SHT,BRUTTO_WEIGHT_OF_KOR,DIMKOR_X*DIMKOR_Y*DIMKOR_Z,CELL from RRL_ARTICULS where ACTICUL='QPOOL2e9b6614d9'");name,barcode,mass,size,cell=q.fetchone()
 ids=[]
 for index in (1,2):
  uid=uid_prefix+"."+str(index)
  pid=q.callfunc("RRL_SBORKA_PALLETS_ADD2",oracledb.DB_TYPE_NUMBER,[number,address,index,uid,"1",datetime(2026,10,14),"","admin",ware]);assert pid>0
  rid=q.callfunc("RRL_SBORKA_PALLET_ROWS_ADD4",oracledb.DB_TYPE_NUMBER,[uid,"QPOOL2e9b6614d9",name,barcode,"EA",mass,cell,mass,size,24,0,None,number,ware,1]);assert rid>0
  ids.append(int(pid))
 c.commit()
 data={"tag":tag,"number":number,"trip":trip,"ware":ware,"ids":ids,"uids":[uid_prefix+".1",uid_prefix+".2"],"quantity":48,"test_data":"Existing synthetic DS-BASE logistics, planning only; no SAP demand, stock or actual cargo claimed"}
 p.write_text(json.dumps(data,ensure_ascii=True),encoding="utf-8")
 result=q.var(oracledb.DB_TYPE_CLOB);sts=q.var(oracledb.DB_TYPE_CLOB);sts.setvalue(0,json.dumps([number]))
 q.callproc("RRL_TRANSPORT_PLAN_API.assign_sts",[trip,sts,"admin",result]);assert read_oracle_json(result.getvalue())["assigned"]==1
 c.rollback();q.execute("select count(*)from RRL_SBORKA_PALLETS where ST_NUMBER=:number and nvl(TRANSTASK_ID,0)=0",number=number);assert q.fetchone()==(2,)
result=assign_validated_sts(OracleGateway(),trip,[number],"admin");assert result["written_sts"]==1
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 response=client.post(f"http://127.0.0.1:8088/api/admin/transport/tasks/{trip}/sts",json={"st_numbers":[number]})
 assert response.status_code==200,response.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_SBORKA_PALLETS where ST_NUMBER=:number and TRANSTASK_ID=:trip_id",number=number,trip_id=trip);assert q.fetchone()==(2,)
 q.execute("select sum(QUANTITY),sum(ORDER_WEIGHT),sum(PACK_COUNT)from RRL_SBORKA_PALLET_ROWS where DOCID=:number",number=number);assert q.fetchone()==(48,20,2)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select executions,round(elapsed_time/1000/nullif(executions,0),3)from V$SQL where SQL_TEXT like '%COUNT(CASE WHEN CONDITION=2%'and executions>0");print("SQL_MS",q.fetchall())
print("PASS270 existing two-pallet same-ST native assign/outer rollback/actual API repeat/48planned20kg2packs preserved/P20H20/no stock writer or newtrip")
