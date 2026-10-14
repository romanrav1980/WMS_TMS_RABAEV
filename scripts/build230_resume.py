from pathlib import Path
import json
s=Path("scripts/ni053_marked_disposition_case.py").read_text(encoding="utf-8");prefix=s[:s.index(' preview=')]
scan=s[s.index(' q.execute("select UNIT_ID'):s.index(' assert len(scans)')]
middle=' q.execute("select OPERATION_ID,CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID like \'STORE230.RECEIVE:%\'and STATE=\'APPLIED\'");op,raw=q.fetchone();canonical=read_oracle_json(raw);winner={"operation_id":op,**canonical["source"],**canonical["metadata"]};winner.pop("unit_scans");winner["scans"]=scans;saved=api(client,"POST",path+"/confirm",winner)\n'
tail=s[s.index(' q.execute("select UNIT_DISPOSITION,sum(BASE_QTY),min'):].replace('after["quantities"][0]["unreceived"]=="1"','after["quantities"][0]["unreceived"]=="0"and after["quantities"][0]["missing"]=="1"')
tail=tail.replace('customer shipped3 accepted2 unreceived1','customer shipped3 accepted2 missing1 unreceived0/PARTIALLY_ACCEPTED')
print(json.dumps({"scripts/resume230_case.py":prefix+scan+middle+tail},ensure_ascii=True))
