from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/public.py");s=p.read_text(encoding="utf-8")
s+="\nfrom .api.st_deferral_routes import router as st_deferral_router\nfrom .contracts_st_deferral import st_deferral_service,StDeferralPort\nfrom .infrastructure.st_deferral import StDeferral\n\ndef build_st_deferral(gateway: Any) -> StDeferralPort:\n    return StDeferral(gateway)\n";out[str(p)]=s
out["api/wms_api_server/app/st_deferral_composition.py"]="from .oracle_gateway import OracleGateway\nfrom .modules.transport.public import build_st_deferral,StDeferralPort\n\ndef build_st_deferral_service() -> StDeferralPort:\n    return build_st_deferral(OracleGateway())\n"
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8")
s+="\nfrom .modules.transport.public import st_deferral_router,st_deferral_service\nfrom .st_deferral_composition import build_st_deferral_service\napp.include_router(st_deferral_router)\napp.dependency_overrides[st_deferral_service]=build_st_deferral_service\n";out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
