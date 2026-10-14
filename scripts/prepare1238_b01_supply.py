"""One retained supply document for the existing order2135; no direct stock writes."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,xml.etree.ElementTree as ET
p=Path("tmp/context1238.json")
x=json.loads(Path("tmp/context1118.json").read_text(encoding="utf-8"))
if p.exists():raise SystemExit("Retained source exists; resume from context1238, do not recreate")
ctx={"stage":"PREPARED","customer_order":2135,"warehouse":9807,"articles":x["articles"],"tag":x["tag"],"barcodes":["QA1118"+x["tag"]+str(i)for i in range(2)]}
root=ET.Element("WarehouseSupplyOrder",version="2")
for k,v in {"Sender":"OWN.QA.SAP","MessageId":"B01.SUPPLY1238:"+x["tag"],"OrderNumber":"B01.1238:"+x["tag"],"Revision":1,"WarehouseId":9807,"ReceiveCell":"CPT_9807","Supplier":"DEV B01 end-to-end retained supply"}.items():ET.SubElement(root,k).text=str(v)
lines=ET.SubElement(root,"Lines")
for i,a in enumerate(x["articles"]):
 line=ET.SubElement(lines,"Line");ET.SubElement(line,"LineNumber").text=str(i+1);ET.SubElement(line,"Material").text=a;ET.SubElement(line,"Quantity",unit="EA").text="18"
ctx["xml"]=ET.tostring(root,encoding="unicode")
p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,PASS from RUSERS where ID='admin' and nvl(DELETED,0)=0");actor,password=q.fetchone()
with httpx.Client(auth=(actor,password),base_url="http://127.0.0.1:8088",timeout=30)as client:
 r=client.post("/api/integrations/sap/supply-orders",content=ctx["xml"].encode(),headers={"Content-Type":"application/xml"})
 assert r.status_code==202,(r.status_code,r.text)
 ctx.update(stage="IMPORTED",supply=r.json())
 p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
 print(json.dumps({"stage":ctx["stage"],"source":ctx["supply"],"customer_order":2135}))
