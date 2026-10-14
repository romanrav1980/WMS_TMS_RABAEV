import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];out={}
p=r/"api/wms_api_server/app/modules/inventory/contracts_case_return.py";s=p.read_text(encoding="utf-8")
s=s.replace("from pydantic import BaseModel, Field","from pydantic import BaseModel, Field, StrictBool, model_validator")
s+='''    allow_empty: StrictBool = False
    reason: str | None = Field(default=None, min_length=1, max_length=1000)

    @model_validator(mode="after")
    def validate_empty_decision(self) -> "CaseCarrierReturnRequest":
        if self.allow_empty:
            if self.destinations or not (self.reason or "").strip():
                raise ValueError("Empty cancellation requires no destinations and an explicit reason")
        elif not 1 <= len(self.destinations) <= 200:
            raise ValueError("Scanned destinations required for a physical return")
        if len(self.destinations) > 200 or any(not k or not v or len(v) > 60 for k, v in self.destinations.items()):
            raise ValueError("Bounded scanned destinations required")
        return self
'''
out[str(p.relative_to(r))]=s
p=r/"api/wms_api_server/app/modules/inventory/public.py";s=p.read_text(encoding="utf-8")
s=s.replace('if not 1 <= len(request.destinations) <= 200 or any(not k or not v or len(v)>60 for k,v in request.destinations.items()):',
 'if not (0 if request.allow_empty else 1) <= len(request.destinations) <= 200 or any(not k or not v or len(v)>60 for k,v in request.destinations.items()):')
s=s.replace('metadata=request.model_dump(mode="json",exclude={"operation_id"})))',
 '''metadata={**request.model_dump(mode="json",exclude={"operation_id","allow_empty","reason"}),
                  **({"allow_empty":True,"reason":request.reason} if request.allow_empty else {})}))''')
out[str(p.relative_to(r))]=s
print(json.dumps(out))
