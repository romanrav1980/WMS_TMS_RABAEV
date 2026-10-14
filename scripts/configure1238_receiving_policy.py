exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
ctx=json.loads(Path("tmp/context1238.json").read_text(encoding="utf-8"));assert ctx["stage"]=="IMPORTED"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,PASS from RUSERS where ID='admin' and nvl(DELETED,0)=0");actor,password=q.fetchone()
with httpx.Client(auth=(actor,password),base_url="http://127.0.0.1:8088",timeout=20)as client:
 for article in ctx["articles"]:
  url="/api/finished-goods/skus/"+article+"/receiving-policy"
  r=client.get(url);r.raise_for_status();policy=r.json()
  if policy["configured"]:
   assert not policy["marking_required"],policy
  else:
   r=client.put(url,json={"expected_version":policy["version"],"marking_required":False,"profiles":[],"serialized_weight_boxes":False,"stack_stage":"MAIN"})
   r.raise_for_status()
  print(json.dumps({"article":article,"configured":True,"marking_required":False}))
