from pathlib import Path
import json
out={};p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_shortage.py");s=p.read_text(encoding="utf-8")
start=s.index("        recovery=None");end=s.index("        recovered_keys=set()",start)
block=s[start:end]
s=s[:start]+"        recovery,placement_plan,placement=read_recovery(cur,claim)\n"+s[end:]
s=s.replace("from ..contracts_store_returns import StoreReturnReceiveError","from ..contracts_store_returns import StoreReturnReceiveError\nfrom .interwarehouse_recovery_read import read_recovery",1)
out[p.as_posix()]=s
body="\n".join(line[4:]if line.startswith("    ")else line for line in block.splitlines())
out["api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_recovery_read.py"]='"""Recovery decision and placement reads on the caller existing RO snapshot."""\nfrom typing import Any\nfrom ..contracts_store_returns import StoreReturnReceiveError\n\ndef read_recovery(cur: Any,claim: tuple|None) -> tuple:\n'+body+"\n    return recovery,placement_plan,placement\n"
print(json.dumps(out))
