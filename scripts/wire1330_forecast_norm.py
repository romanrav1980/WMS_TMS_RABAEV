from pathlib import Path
p=Path("api/wms_api_server/app/modules/resources/public.py");s=p.read_text(encoding="utf-8")+"\nfrom .infrastructure.forecast_norms import forecast_norm_basis\nfrom .domain.forecast_labour import forecast_labour\n";p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/transport/infrastructure/warehouse_forecast.py");s=p.read_text(encoding="utf-8")
s=s.replace("from .forecast_projection import ForecastProjection","from .forecast_projection import ForecastProjection\nfrom ...resources.public import forecast_norm_basis,forecast_labour")
s=s.replace("series=self._series(cur,window,query.scope)","series=self._series(cur,window,query.scope)\n            norm_basis=forecast_norm_basis(cur,ware,query.scope,series)")
s=s.replace('signature=sha256(', 'labour=forecast_labour(predictions,norm_basis)\n        signature=sha256(',1)
s=s.replace('"observed_days":days,"series":predictions,','"observed_days":days,"series":predictions,"labour_estimate":labour,\n            "norm_data_signature":sha256(json.dumps(norm_basis,sort_keys=True,separators=(",",":")).encode()).hexdigest(),')
p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/resources/infrastructure/workload_config.py");s=p.read_text(encoding="utf-8")
s=s.replace("norms=workload_rows(cur)","norms=workload_rows(cur)\n            cur.execute(\"select s.WORK_SCOPE,s.SITE_CODE,s.VERSION_NO,s.ACTIVE,s.REASON,s.OPERATION_ID from RRL_WORKLOAD_SCOPE_SITE s where s.WARE_ID=:ware and s.VERSION_NO=(select max(x.VERSION_NO)from RRL_WORKLOAD_SCOPE_SITE x where x.WARE_ID=s.WARE_ID and x.WORK_SCOPE=s.WORK_SCOPE)order by s.WORK_SCOPE\",ware=ware)\n            forecast_scopes=workload_rows(cur)")
s=s.replace('"norms":norms,','"norms":norms,"forecast_scopes":forecast_scopes,')
p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/resources/api/workload_config_routes.py");s=p.read_text(encoding="utf-8").replace("from typing import Any","from typing import Any,Literal")
s+="""

class ForecastScopeInput(CommandInput):
    work_scope: Literal["CASE_DISPATCH","FULLPAL_DISPATCH","OUTBOUND_WORKLOAD"]
    site_code: str=Field(strict=True,min_length=1,max_length=50)
    expected_version: int=Field(strict=True,ge=0)
    active: bool=Field(strict=True)

@router.post("/forecast-scopes")
def save_forecast_scope(request: ForecastScopeInput,user: AdminUser=Depends(require_permission("resource_shift_edit")),service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str,Any]:
    return invoke(request,"FORECAST_SCOPE",user,service)
"""
p.write_text(s,encoding="utf-8")
