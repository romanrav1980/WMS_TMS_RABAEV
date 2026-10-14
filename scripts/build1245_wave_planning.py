from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/services/picking_service.py");s=p.read_text(encoding="utf-8")
a=s.index("    def create_wave(");b=s.index("    def preview_wave(",a)
s=s[:a]+'''    def create_wave(self, request: PickWaveCreateRequest) -> int:
        from ..modules.inventory.public import create_existing_wave
        return create_existing_wave(self.gateway, request)

    def add_wave_plan(self, pick_wave_id: int, request: PickWaveAddPlanRequest) -> None:
        from ..modules.inventory.public import add_existing_wave_plan
        return add_existing_wave_plan(self.gateway, pick_wave_id, request)

'''+s[b:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
s+='\nfrom .infrastructure.wave_planning import create_wave as create_existing_wave, add_plan as add_existing_wave_plan\n';out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
