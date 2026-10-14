import ast,json,subprocess
from pathlib import Path
source=subprocess.check_output(["git","show","HEAD:api/wms_api_server/app/schemas.py"]).decode("utf-8")
tree=ast.parse(source);lines=source.splitlines(keepends=True)
nodes=[n for n in tree.body if isinstance(n,ast.ClassDef)and n.name in{"StockReservationCreateRequest","StockReservationPromoteRequest","StockReservationStatusRequest"}]
assert len(nodes)==3
models="\n\n".join("".join(lines[n.lineno-1:n.end_lineno])for n in nodes)
content='"""Passive public inventory DTOs; schemas.py retains compatibility aliases."""\nfrom decimal import Decimal\nfrom pydantic import BaseModel, Field\nfrom .contracts_case_short import CasePickShortDecisionRequest\n\n'+models+"\n"
print(json.dumps({"api/wms_api_server/app/modules/inventory/contracts.py":content},ensure_ascii=True))
