from pathlib import Path
import json
s=Path("scripts/ni062_marked_approval_case.py").read_text(encoding="utf-8")
prefix=s[:s.index(' dossier=')]
middle=''' q.execute("select OPERATION_ID,CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID like 'RET231.APP:%'and STATE='APPLIED'");op,raw=q.fetchone()
 from app.modules.platform.public import read_oracle_json
 canonical=read_oracle_json(raw);winner=dict(canonical["metadata"],line_no=canonical["source"]["line_no"],operation_id=op);saved=api(client,"POST",path+receipt+"/approve",winner)
 second={"operation_id":"RET231.DISPOSAL:"+tag};legacy_body={"operation_id":"RET231.LEGACY:13508027ed"}
 q.execute("select PHYSICAL_UNIT_KEY from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=:p and UNIT_DISPOSITION='MISSING'",p=receipt);missing=q.fetchone()[0]
'''
tail=s[s.index(' q.execute("update RUSERS set DELETED=1'):].replace('winner,403)','winner,401)')
print(json.dumps({"scripts/resume231_case.py":prefix+middle+tail},ensure_ascii=True))
