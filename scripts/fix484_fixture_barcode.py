import json
from pathlib import Path
p=Path("scripts/case483_exception_returns.py");s=p.read_text(encoding="utf-8")
old=' q.execute("select BARCODE_SHT from RRL_ARTICULS where ACTICUL=:a",a=article);barcode=q.fetchone()[0]'
new=''' # Retained QA item GTIN is shared with other QA articles. Use its own existing
 # box barcode; preserve GS1 codes and the strict unique barcode resolver.
 barcode="QBOX483"+tag
 config(lambda:q.execute("update RRL_ARTICULS set BARCODE_KOR=:bc where ACTICUL=:a",bc=barcode,a=article))'''
assert s.count(old)==1;s=s.replace(old,new).replace('operation_id="EXRET483.RECEIVE:"','operation_id="EXRET483.RECEIVE2:"')
print(json.dumps({str(p):s}))
