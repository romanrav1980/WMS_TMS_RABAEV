import json
from pathlib import Path
p=Path("scripts/case483_exception_returns.py");s=p.read_text(encoding="utf-8")
marker=' config(lambda:q.execute("update RRL_ARTICULS set BARCODE_KOR=:bc where ACTICUL=:a",bc=barcode,a=article))'
s=s.replace(marker,marker+'''
 q.execute("select to_char(p.EXPIRY_DATE,'YYYY-MM-DD'),r.SUPPLIER_BATCH from RRL_PALLETS p join RRL_SAP_PALLET_RECEIPT r on r.UID_PALLET=nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET)where p.UID_PALLET=:p_uid",p_uid=lot)
 expiry,batch=q.fetchone()
''')
s=s.replace('operation_id="EXRET483.RECEIVE2:"','operation_id="EXRET483.RECEIVE3:"').replace('expiry_date="2030-01-01",supplier_batch="DEV483:"+tag','expiry_date=expiry,supplier_batch=batch')
print(json.dumps({str(p):s}))
