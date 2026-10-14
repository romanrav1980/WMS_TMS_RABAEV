from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/master_data/contracts.py");v=p.read_text(encoding="utf-8")
v=v.replace("from typing import Literal","from typing import Literal, Annotated").replace("Field, model_validator","Field, model_validator, AfterValidator")
a="class MarkingProfile(BaseModel):"
b='''def _profile_storage_value(value: str) -> str:
    """Native profile identity columns and resolvers use VARCHAR2(80 BYTE)."""
    if len(value.encode("utf-8")) > 80:
        raise ValueError("Profile code exceeds native UTF-8 storage limit of 80 bytes.")
    return value


MarkingProfileCode = Annotated[str, Field(strict=True, min_length=1, max_length=80),
    AfterValidator(_profile_storage_value)]


class MarkingProfile(BaseModel):'''
assert a in v;v=v.replace(a,b).replace('profile_code: str = Field(min_length=1, max_length=80)','profile_code: MarkingProfileCode');out[str(p)]=v
files={"delivery/api/store_receipt_routes.py":"...","inventory/contracts_aggregation_scans.py":"..","inventory/api/inventory_count_routes.py":"...","inventory/api/task_scan_routes.py":"...","inventory/api/trace_manifest_routes.py":"..."}
for name,dots in files.items():
 p=Path("api/wms_api_server/app/modules")/name;v=p.read_text(encoding="utf-8")
 lines=v.splitlines()
 changed=False
 for i,line in enumerate(lines):
  if "profile_code:"in line and "Field("in line:
   lines[i]=line[:len(line)-len(line.lstrip())]+"profile_code: MarkingProfileCode";changed=True
 assert changed,name
 v="\n".join(lines)+"\n"
 v="from "+dots+"master_data.contracts import MarkingProfileCode\n"+v
 out[str(p)]=v
print(json.dumps(out,ensure_ascii=True))
