from pathlib import Path
import json
old=Path("scripts/source291_ordinary_case.py").read_text(encoding="utf-8");out={}
for num in ["328","329"]:
 s=old.replace("291",num).replace("q.execute('select min(TRANSPORTTYPE) from RRL_TRANSPORT_TYPE')","q.execute(\"select TRANSPORTTYPE from RRL_TRANSPORT_TYPE where TRANSPORTTYPE='15'\")")
 if num=="329":
  start=s.index("        target = ware + 50000000")
  end=s.index("        now = datetime.now",start)
  s=s[:start]+"""        common=json.loads(Path('tmp/context328.json').read_text(encoding='utf-8'))
        target=common['target_warehouse'];inbound=common['inbound'];outbound=common['outbound'];target_trip=common['target_trip']
"""+s[end:]
 out["scripts/source"+num+"_ordinary_case.py"]=s
print(json.dumps(out))
