import json
from pathlib import Path
p=Path("api/wms_api_server/app/services/picking_service.py");s=p.read_text(encoding="utf-8")
a=s.index("    def release_wave_staging(");b=s.index("    def _validate_pick_task_scans",a)
replacement='''    def release_wave_staging(self, pick_wave_id: int, request: PickWaveStagingReleaseRequest) -> int:
        from ..modules.inventory.public import release_existing_wave_staging
        return release_existing_wave_staging(self.gateway, pick_wave_id, request)

'''
files={str(p):s[:a]+replacement+s[b:]}
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
s+="\nfrom .infrastructure.wave_staging import release_staging as release_existing_wave_staging\n";files[str(p)]=s
p=Path("api/wms_api_server/app/routers/picking.py");s=p.read_text(encoding="utf-8")
old="    released_count = PickingService().release_wave_staging(pick_wave_id, request)"
assert s.count(old)==1
s=s.replace(old,'''    try:
        released_count = PickingService().release_wave_staging(pick_wave_id, request)
    except WavePlanningError as exc:
        raise HTTPException(exc.status_code, detail={"code": exc.code}) from exc''')
# Use the established domain exception attribute, do not assume its spelling.
error=Path("api/wms_api_server/app/modules/inventory/contracts_wave_planning.py").read_text()
if "self.status =" in error:s=s.replace("raise HTTPException(exc.status_code, detail", "raise HTTPException(exc.status, detail")
files[str(p)]=s
print(json.dumps(files))
