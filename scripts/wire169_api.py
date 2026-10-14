import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];out={}
p=r/"api/wms_api_server/app/modules/inventory/infrastructure/wave_execution_reader.py"
s=p.read_text(encoding="utf-8");start=s.index("    cur.execute(",s.index("def assert_wave_view"));end=s.index("\n\n\ndef execution_snapshot",start)
s=s[:start]+"""    import oracledb
    try:
        cur.callproc("RRL_WAVE_EXEC_ACCESS.assert_scope", [wave, actor, "pick_wave_view"])
    except oracledb.DatabaseError as exc:
        code = getattr(exc.args[0], "code", 0)
        if code == 20882:
            raise HTTPException(403, detail="WAVE_CURRENT_WARE_VIEWER_REQUIRED") from exc
        if code == 20886 and "WAVE_IDENTITY_MISSING" in str(exc.args[0]):
            raise HTTPException(404, detail="WAVE_NOT_FOUND") from exc
        raise
"""+s[end:]
s=s.replace('data["physical_stock_changed"] = False','''cur.execute("select RRL_WAVE_EXEC_ACCESS.deferred_snapshot_json(:p_wave)from dual", p_wave=wave)
        raw = cur.fetchone()[0]
        data["deferred_decision"] = json.loads(raw.read() if hasattr(raw, "read") else raw)
        data["physical_stock_changed"] = False''')
out[str(p.relative_to(r))]=s
p=r/"api/wms_api_server/app/modules/inventory/api/wave_execution_routes.py";s=p.read_text(encoding="utf-8")
s=s.replace("from typing import Protocol","from typing import Protocol, Literal").replace("from pydantic import BaseModel, Field","from pydantic import BaseModel, Field, ConfigDict, model_validator")
s=s.replace("def finish(self, wave_id: int, operation_id: str, actor: str) -> dict: ...","def finish(self, wave_id: int, operation_id: str, actor: str, disposition: str | None = None, reason: str | None = None) -> dict: ...")
needle='class FinishRequest(BaseModel):'
s=s.replace(needle,needle+'''
    model_config = ConfigDict(extra="forbid")
    disposition: Literal["RETURNED_TO_PLANNING"] | None = None
    reason: str | None = Field(default=None, min_length=1, max_length=1000)

    @model_validator(mode="after")
    def require_reason(self) -> "FinishRequest":
        if self.disposition and not (self.reason or "").strip():
            raise ValueError("Reason required for returned demand")
        return self
''')
s=s.replace("return service.finish(wave_id, body.operation_id, user.username)","return service.finish(wave_id, body.operation_id, user.username, body.disposition, body.reason)")
out[str(p.relative_to(r))]=s
p=r/"api/wms_api_server/app/modules/inventory/infrastructure/wave_execution.py";s=p.read_text(encoding="utf-8")
s=s.replace("def finish(self, wave_id: int, operation_id: str, actor: str) -> dict:","def finish(self, wave_id: int, operation_id: str, actor: str, disposition: str | None = None, reason: str | None = None) -> dict:")
s=s.replace('lines=(), source={"wave_id": wave_id}, metadata={}))','lines=(), source={"wave_id": wave_id}, metadata=({"disposition": disposition, "reason": reason} if disposition else {})))')
out[str(p.relative_to(r))]=s
print(json.dumps(out))
