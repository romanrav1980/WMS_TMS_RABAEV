from pathlib import Path
import json,httpx
ctx=json.loads(Path("tmp/context744.json").read_text(encoding="utf-8"))
url="http://127.0.0.1:8088/api/transport/st-deferrals/trip-candidates"
with httpx.Client(auth=("admin","admin123"),timeout=30)as c:
 params={"st_number":ctx["st_uid"]}
 r=c.get(url,params=params);assert r.status_code==200,r.text
 result=r.json()
 assert all(row["trip_id"]!=ctx["ids"][-1]and row["shipment_date"]>=result["minimum_date"] for row in result["rows"])
 print("CANDIDATES",[(r["trip_id"],r["shipment_date"],r["districts"],r["stores"])for r in result["rows"]])
 for fields,status in (({"limit":101},422),({"date_from":"2026-10-14","date_to":"2026-12-14"},422),({"after_date":"2026-10-14T00:00:00"},422),({"date_from":"2026-10-01","date_to":"2026-10-02"},422)):
  r=c.get(url,params=dict(params,**fields));assert r.status_code==status,r.text
 r=c.get(url,params=dict(params,store_code="NO_SUCH_STORE794"));assert r.status_code==200 and r.json()["rows"]==[],r.text
 r=c.get(url,params=dict(params,district="NO_SUCH_DISTRICT794"));assert r.status_code==200 and r.json()["rows"]==[],r.text
 positives=[]
 for row in result["rows"]:
  if row["districts"]:
   r=c.get(url,params=dict(params,district=row["districts"][0]));assert r.status_code==200 and any(x["trip_id"]==row["trip_id"]for x in r.json()["rows"]),r.text;positives.append("district");break
 for row in result["rows"]:
  if row["stores"]:
   r=c.get(url,params=dict(params,store_code=row["stores"][0]));assert r.status_code==200 and any(x["trip_id"]==row["trip_id"]for x in r.json()["rows"]),r.text;positives.append("store");break
 Path("tmp/context794.json").write_text(json.dumps({"source_st":ctx["st_uid"],"result":result,"positive_filters":positives}),encoding="utf-8")
print("794 PASS bounded current TMS picker/date guards/cursor guard/missing district-store; positive filters:",positives)
