exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import httpx
with httpx.Client(auth=("admin","admin123"),timeout=30)as h:
 for number in[291,292]:
  x=json.loads(Path("tmp/context296_"+str(number)+".json").read_text());r=h.get("http://127.0.0.1:8088/api/delivery/store-receipts/preview",params=dict(load_operation_id=x["load_operation_id"],store_address=x["onward_result"]["final_address"]))
  assert r.status_code==200,r.text
  preview=r.json();Path("tmp/preview297_"+str(number)+".json").write_text(json.dumps(preview,indent=2),encoding="utf-8")
  print(number,dict(mode=preview.get("mode"),root=preview.get("root"),marked=preview.get("requires_marked_recipient_flow"),keys=list(preview),qty=preview["snapshot"]["nodes"][0]["quantity"]))
