from pathlib import Path
import json
old=Path("scripts/case994_hu_binding.py").read_text(encoding="utf-8")
head=old[:old.index('assert not path.exists()')]
head+='record=json.loads(path.read_text(encoding="utf-8"));assert record["stage"]=="CREATED","Retained phase required"\nroot=record["root"]\ndef save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")\ng=OracleGateway();hu=WarehouseHu(g)\n'
tail=old[old.index("with oracledb.connect("):]
tail=tail.replace('"scan_child":carrier}', '"scan_child":carrier,"retained_tare_booking_operation_id":"TARE987.BOOK:"+ctx["tag"]+":"+str(caseid)}',1)
tail=tail.replace('"HU994.ATTACH:"','"HU995.ATTACH:"')
print(json.dumps({"scripts/resume995_hu_binding.py":head+tail},ensure_ascii=True))
