exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
r={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 q.execute("select TABLE_NAME,COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME in('RRL_ARTICULS','RRL_FINISHED_GOODS_SKU','RRL_TR_VEHICLE','RRL_TRANSPORT_TASK','RRL_CUSTOMER_ORDER','RRL_SAP_STORE_ORDER')and(COLUMN_NAME like '%TEMP%'or COLUMN_NAME like '%COLD%'or COLUMN_NAME like '%DEADLINE%'or COLUMN_NAME like '%DOCK%')order by TABLE_NAME,COLUMN_ID");r["existing_constraint_columns"]=[list(x)for x in q]
 q.execute("select ID,TRANSPORT,CONDITION,DELETED,PAY_ORDER_ID from RRL_TRANSPORT_TASK where ID=33571");r["retained_own_trip"]=list(q.fetchone())
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin","admin123"),timeout=20)as c:
 response=c.post("/api/transport/preflight/trips/33571",json={"additional_st_numbers":["SAP_2135"]})
 r["preflight_status"]=response.status_code;r["preflight"]=response.json()
 assert response.status_code==200,response.text
 assert r["preflight"]["read_only"] and r["preflight"]["operational_admission"] is False
Path("tmp/read1132_transport_constraints.json").write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(r,ensure_ascii=True,default=str))
