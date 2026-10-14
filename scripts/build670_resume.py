import json
from pathlib import Path
s=Path("scripts/source670_group_agg.py").read_text(encoding="utf-8")
prefix=s[:s.index('if Path("tmp/context670')]
opening=s[s.index("with oracledb.connect"):s.index(' q.execute("select user')]
body=""" ctx=json.loads(Path("tmp/source670_progress.json").read_text(encoding="utf-8"))
 globals().update(ctx);ware=ctx["warehouse"];gtin=ctx["barcode"];receive="QR670"+tag;pick="QK670"+tag
 import httpx
 from app.modules.platform.public import read_oracle_json
 admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
 def api(method,path,body=None,status=200):
  r=admin_api.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1600]);return r.json()
 q.execute("select RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op and STATE='APPLIED'",op="IW670.BIRTH:"+tag);born=read_oracle_json(q.fetchone()[0])
 # A private equal-distance fixture selected another empty storage cell correctly.
 # Give this SKU's private pick face and intended storage a distinct coordinate, then use existing replan.
 for cell in(src,pick):meta("update RRL_CELLS set X=100 where CELL=:cell and WARE_ID=:ware",cell=cell)
 replanned=api("POST","/api/receiving/putaway/"+str(born["task_id"])+"/replan",dict(operation_id="IW670.REPLAN:"+tag,scanned_pallet=lot,scanned_from_cell=receive,reason="Private SKU pick-face coordinates; nearest free storage"))
 assert replanned["placement"]["cell"]==src,replanned
 try:
"""
start=s.index('  api("POST","/api/receiving/putaway/')
tail=s[start:]
# Only the already-created birth is resumed; no original supplier/seed factory is repeated.
print(json.dumps({"scripts/resume670_group_agg.py":prefix+opening+body+tail}))
