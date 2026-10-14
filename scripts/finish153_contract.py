from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/integrations/contracts_regulatory.py");text=p.read_text(encoding="utf-8")
start=text.index("@dataclass(frozen=True)");end=text.index("class RegulatoryAdapter(Protocol):")
model=text[start:end];text=text[:start]+"from .domain.regulatory_delivery import RegulatoryResponse\n\n"+text[end:]
text=text.replace("from dataclasses import dataclass\n","")
q=Path("api/wms_api_server/app/modules/integrations/domain/regulatory_delivery.py");domain=q.read_text(encoding="utf-8")
domain=domain.replace("from ..contracts_regulatory import RegulatoryResponse",model.rstrip())
print(json.dumps({str(p):text,str(q):domain},ensure_ascii=True))
