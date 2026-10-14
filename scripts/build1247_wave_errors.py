from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/wave_planning.py");s=p.read_text(encoding="utf-8")
s=s.replace("from fastapi import HTTPException","from ..contracts_wave_planning import WavePlanningError")
for status,code in [(422,"WAVE_EXPLICIT_WAREHOUSE_REQUIRED"),(403,"WAVE_CURRENT_WAREHOUSE_REQUIRED"),(404,"PICK_PLAN_NOT_FOUND"),(404,"PICK_WAVE_NOT_FOUND"),(409,"PICK_PLAN_WAVE_WAREHOUSE_MISMATCH")]:
 s=s.replace(f'HTTPException({status}, detail="{code}")',f'WavePlanningError("{code}", {status})')
s=s.replace('HTTPException(409, detail=str(exc.args[0]).split("\\n", 1)[0])','WavePlanningError(str(exc.args[0]).split("\\n", 1)[0], 409)')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
s+='\nfrom .contracts_wave_planning import WavePlanningError\n';out[str(p)]=s
p=Path("api/wms_api_server/app/services/picking_service.py");s=p.read_text(encoding="utf-8")
s=s.replace('''        from ..modules.inventory.public import create_existing_wave
        return create_existing_wave(self.gateway, request)''','''        from ..modules.inventory.public import create_existing_wave, WavePlanningError
        try:
            return create_existing_wave(self.gateway, request)
        except WavePlanningError as exc:
            raise HTTPException(exc.status, detail=exc.code) from exc''')
s=s.replace('''        from ..modules.inventory.public import add_existing_wave_plan
        return add_existing_wave_plan(self.gateway, pick_wave_id, request)''','''        from ..modules.inventory.public import add_existing_wave_plan, WavePlanningError
        try:
            return add_existing_wave_plan(self.gateway, pick_wave_id, request)
        except WavePlanningError as exc:
            raise HTTPException(exc.status, detail=exc.code) from exc''')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
