from pathlib import Path
import json
base=Path("api/wms_api_server/app/modules/fulfillment")
files={}
p=base/"infrastructure/legacy_preparation.py"
s=p.read_text(encoding="utf-8")
start=s.index("        digest = sha256",s.index("    def prepare("))
end=s.index("    def _demand(",start)
old=s[start:end]
inner=old[old.index("            cur.execute"):old.rindex("        return result")]
inner="\n".join(line[4:] if line.startswith("    ")else line for line in inner.splitlines())+"\n"
inner=inner.replace("            'status':'ST_PREPARED','layout_source':'OPERATOR','prepared_by':actor,'idempotent':False}", "            'status':'ST_PREPARED','layout_source':'OPERATOR','prepared_by':actor,'idempotent':False}")
needle="        cur.setinputsizes(body=oracledb.DB_TYPE_CLOB)"
inner=inner.replace(needle,"        if result_metadata:\n            result.update(result_metadata)\n"+needle)
new='''        with source_transaction(self.gateway,'SAP demand to existing legacy ST preparation',actor,'customer_order_import',order=order_id) as cur:
            from .automatic_preparation import lock_layout_inputs
            lock_layout_inputs(cur, order_id)
            return self._prepare_locked(cur, order_id, payload, actor)

    def auto_preview(self, order_id: int, limits: dict, actor: str) -> dict:
        from .automatic_preparation import AutomaticPreparation
        return AutomaticPreparation(self).preview(order_id, limits, actor)

    def auto_prepare(self, order_id: int, payload: dict, actor: str) -> dict:
        from .automatic_preparation import AutomaticPreparation
        return AutomaticPreparation(self).prepare(order_id, payload, actor)

    def auto_resolve(self, order_id: int, payload: dict, actor: str) -> dict:
        from .automatic_preparation import AutomaticPreparation
        return AutomaticPreparation(self).resolve(order_id, payload, actor)

    def _prepare_locked(self, cur, order_id: int, payload: dict, actor: str, result_metadata: dict | None = None) -> dict:
        digest = sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
'''+inner+"        return result\n\n"
files[str(p)]=s[:start]+new+s[end:]
p=base/"infrastructure/preparation_readiness.py";s=p.read_text(encoding="utf-8")
s=s.replace("order: int, actor: str)","order: int, actor: str, permission: str = \"customer_order_view\")")
s=s.replace('        cur.execute("set transaction read only")','        if not getattr(gateway, "transaction_bound", False):\n            cur.execute("set transaction read only")')
s=s.replace('actor, "customer_order_view"','actor, permission').replace('actor,"customer_order_view"','actor,permission')
files[str(p)]=s
p=base/"application/ports.py";s=p.read_text(encoding="utf-8")
s=s.replace("class PreparationPort(Protocol):","class PreparationPort(Protocol):\n    def auto_preview(self, order_id: int, limits: dict, actor: str) -> dict: ...\n    def auto_prepare(self, order_id: int, payload: dict, actor: str) -> dict: ...\n    def auto_resolve(self, order_id: int, payload: dict, actor: str) -> dict: ...")
files[str(p)]=s
p=base/"api/preparation_read_routes.py";s=p.read_text(encoding="utf-8")
s+='''

from decimal import Decimal
from ..domain.automatic_layout import STRATEGY
class AutoLimits(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_goods_weight_kg: Decimal = Field(gt=0, max_digits=18, decimal_places=6, allow_inf_nan=False)
    max_goods_volume_m3: Decimal = Field(gt=0, max_digits=18, decimal_places=9, allow_inf_nan=False)
    max_pallets: int = Field(strict=True, ge=1, le=100)

class AutoPreparationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    source_signature: str = Field(pattern=r"^[a-f0-9]{64}$")
    limits: AutoLimits

def auto_call(method, order_id, body, user):
    try:
        return method(order_id, body, user.username)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc

@router.post("/{order_id}/automatic-layout")
def auto_preview(order_id: int, body: AutoLimits,
                 user: AdminUser=Depends(require_permission("customer_order_view")),
                 service: PreparationPort=Depends(preparation_service)) -> dict:
    return auto_call(service.auto_preview, order_id, body.model_dump(mode="json"), user)

@router.post("/{order_id}/prepare-st/automatic")
def auto_prepare(order_id: int, body: AutoPreparationRequest,
                 user: AdminUser=Depends(require_permission("customer_order_import")),
                 service: PreparationPort=Depends(preparation_service)) -> dict:
    return auto_call(service.auto_prepare, order_id, body.model_dump(mode="json"), user)

@router.post("/{order_id}/prepare-st/automatic/resolve")
def auto_resolve(order_id: int, body: AutoPreparationRequest,
                 user: AdminUser=Depends(require_permission("customer_order_import")),
                 service: PreparationPort=Depends(preparation_service)) -> dict:
    return auto_call(service.auto_resolve, order_id, body.model_dump(mode="json"), user)
'''
files[str(p)]=s
p=Path("wiki/index.md");files[str(p)]="- [NI02.1: новый автоматический расчёт](components/nicora_ni021_auto_preparation_20261013.md): разрешение владельца, единый legacy writer, явные пределы и точная whole-box укладка.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 / NI02.1 / 1113: зарегистрирован контракт самостоятельного расчёта после разрешения владельца; новый domain algorithm и общий locked legacy writer в разработке. Read1112:2047 готов к ручной подготовке, но NORMA_UKLADKI=1 меньше коробки24; автоматический допуск не обходится.\n"
print(json.dumps(files,ensure_ascii=True))
