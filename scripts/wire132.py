from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/application/ports.py");s=p.read_text(encoding="utf-8")
s=s.replace("def composition(self, pallet: str, after: str = '', limit: int = 50)","def composition(self, pallet: str, after: str = '', limit: int = 50, expected_signature: str | None = None)",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/api/receiving_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ..domain.pallet_identifiers import normalize_incoming_sscc","from ..domain.pallet_identifiers import normalize_incoming_sscc\nfrom ..contracts_composition import CompositionViewError",1)
s=s.replace('def pallet_composition(pallet: str, after: str = "", limit: int = Query(50, ge=1, le=100),','def pallet_composition(pallet: str, after: str = Query("",max_length=64), limit: int = Query(50, ge=1, le=100),\n                        expected_signature: str | None = Query(None,min_length=64,max_length=64),',1)
s=s.replace('return service.composition(pallet, after, limit)','return service.composition(pallet, after, limit,expected_signature)',1)
needle='    except LookupError as exc:\n        raise HTTPException(404, str(exc)) from exc'
assert needle in s;s=s.replace(needle,needle+'\n    except CompositionViewError as exc:\n        raise HTTPException(exc.status,{"code":exc.code}) from exc',1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
s=s.replace('def pallet_composition(pallet: str, after: str = "", limit: int = 50) -> dict:','def pallet_composition(pallet: str, after: str = "", limit: int = 50, expected_signature: str|None=None) -> dict:',1)
s=s.replace('return ReceivingQueries(OracleGateway()).composition(pallet, after, min(max(limit, 1), 100))','return ReceivingQueries(OracleGateway()).composition(pallet, after, min(max(limit, 1), 100),expected_signature)',1);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
