from pathlib import Path
import json
out={};p=Path("api/wms_api_server/app/schemas.py");t=p.read_text(encoding="utf-8")
a=t.index("class CasePickShortDecisionRequest(BaseModel):");b=t.index("\n\nclass PalletTypeUpsertRequest",a)
cls=t[a:b].strip()+"\n";out["api/wms_api_server/app/modules/inventory/contracts_case_short.py"]='"""Existing CASE decision contract with explicit weight tolerance proof."""\nfrom typing import Literal\nfrom pydantic import BaseModel, Field\n\n\n'+cls
out[str(p)]=t[:a]+"from .modules.inventory.contracts_case_short import CasePickShortDecisionRequest\n"+t[b:]
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/case_short_commands.py");out[str(p)]=p.read_text(encoding="utf-8").replace("from ....schemas import CasePickShortDecisionRequest","from ..contracts_case_short import CasePickShortDecisionRequest")
print(json.dumps(out,ensure_ascii=True))
