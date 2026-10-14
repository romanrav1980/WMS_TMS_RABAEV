from pathlib import Path
import json
s=Path("scripts/ni063_fullpal_load_recovery_case.py").read_text(encoding="utf-8");prefix=s[:s.index(" admin_api=")]
body=s[s.index(' q.execute("select PHYSICAL_QTY,HELD_QTY'):].replace("HELD_QTY","ASSEMBLY_QTY")
out={"scripts/resume220_case.py":prefix+' recovery={"operation_id":"TARE220.RECOVERY:"+tag}\n'+body}
p=Path("scripts/ni063_fullpal_load_recovery_case.py");out[str(p)]=s.replace("HELD_QTY","ASSEMBLY_QTY")
p=Path("scripts/build220_case.py");out[str(p)]=p.read_text(encoding="utf-8").replace("HELD_QTY","ASSEMBLY_QTY")
print(json.dumps(out,ensure_ascii=True))
