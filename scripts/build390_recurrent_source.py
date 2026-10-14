from pathlib import Path
import json
t=Path("scripts/source311_marked_case.py").read_text(encoding="utf-8").replace("311","390")
t=t.replace("'BOX',0.125","'BOX',3")
at=t.index(' meta("insert into RRL_STOCK_POLICY_GUARD')
t=t[:at]+''' box_prefix="047"+str(int(tag,16)%10000000000).zfill(10);box_gtin=box_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(box_prefix)))%10)%10)
'''+t[at:]
needle='("E1BPE1MARMRT",dict(ALT_UNIT="EA",NUMERATOR="1",DENOMINATR="1",EAN_UPC=gtin))'
t=t.replace(needle,needle+',("E1BPE1MARMRT",dict(ALT_UNIT="BOX",NUMERATOR="1",DENOMINATR="1",EAN_UPC=box_gtin))')
t=t.replace('"source_quantity":"3",','"source_quantity":"3","box_barcode":box_gtin,"supplier_batch":"PB390:"+tag,"expiry":"2030-01-01","receive":receive,"pick":pick,"order":order,"vehicle":vehicle,"plate":"QL"+tag,"driver":driver,')
t=t.replace('SOURCE390 marked3/6codes/sourceP0/frozenplan; no hardware/gov ACK','SOURCE390 SAPverified3EA/BOX1/sourceP0/frozenfirstleg/same3keys6codes')
out={"scripts/source390_recurrent.py":t}
t=Path("scripts/receive368_initial.py").read_text().replace("368","390");out["scripts/receive390_initial.py"]=t
print(json.dumps(out))
