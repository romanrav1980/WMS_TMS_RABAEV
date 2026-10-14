from pathlib import Path
p=Path("api/wms_api_server/app/modules/resources/public.py")
s=p.read_text(encoding="utf-8-sig")+'''
from .contracts_wave_time import WaveTimePort,wave_time_service
from .api.wave_time_routes import router as wave_time_router
from .infrastructure.wave_time import WaveTime

def build_wave_time(gateway: Any) -> WaveTimePort:
    return WaveTime(gateway)
'''
p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/workload_composition.py")
s=p.read_text(encoding="utf-8-sig")+'''
from .modules.resources.public import WaveTimePort,build_wave_time

def wave_time() -> WaveTimePort:
    return build_wave_time(OracleGateway())
'''
p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/main.py")
s=p.read_text(encoding="utf-8-sig")+'''
from .modules.resources.public import wave_time_router,wave_time_service
from .workload_composition import wave_time
app.include_router(wave_time_router)
app.dependency_overrides[wave_time_service]=wave_time
'''
p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/resources/infrastructure/workload_monitor.py")
s=p.read_text(encoding="utf-8-sig").replace("from .workload_config import current_warehouse,workload_rows","from .workload_config import current_warehouse,workload_rows\nfrom .wave_time_reader import approved_wave_windows")
s=s.replace("            work=self._work(cur,ware,site);attendance=self._attendance(cur,ware,site,start,end)","            work=self._work(cur,ware,site);attendance=self._attendance(cur,ware,site,start,end)\n            approved=approved_wave_windows(cur,ware)")
s=s.replace('row["window"]=(planned["start_at"],planned["finish_at"])if planned else None','''saved=approved.get(int(row["pick_wave_id"]))
            row["window"]=(planned["start_at"],planned["finish_at"])if planned else saved["window"] if saved else None
            row["window_source"]="EXPLICIT_PREVIEW" if planned else saved["status"] if saved else "NO_APPROVED_PLAN"''')
s=s.replace('"window_source":"EXPLICIT_PREVIEW"','"window_source":"EXPLICIT_PREVIEW_OR_APPROVED_PLAN"')
p.write_text(s,encoding="utf-8")
