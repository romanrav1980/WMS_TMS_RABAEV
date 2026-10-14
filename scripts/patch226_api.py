raise SystemExit("Retired authoring generator: use final SQL/current manifest and fresh affected-owner checkpoint; never overwrite later runtime")
from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory");out={}
f=p/"api/interwarehouse_routes.py";s=f.read_text(encoding="utf-8")
s=s.replace('router = APIRouter','from .task_scan_routes import UnitScan\n\nrouter = APIRouter',1)
s=s.replace('class Receive(PhysicalAction):','class Receive(PhysicalAction):\n    scans: list[UnitScan] = Field(default_factory=list,max_length=20000)')
s=s.replace('body.model_dump(exclude={"operation_id","plan_operation_id"})','body.model_dump(exclude={"operation_id","plan_operation_id"},exclude_defaults=True)')
s+='\n@router.get("/plans/{plan_id}/units")\ndef source_units(plan_id: str,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:\n    try:\n        return service.unit_manifest(plan_id,user.username)\n    except StoreReturnReceiveError as exc:\n        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc\n'
out[str(f)]=s
f=p/"contracts_interwarehouse.py";s=f.read_text(encoding="utf-8").replace('    def queue(', '    def unit_manifest(self, plan_id: str, actor: str) -> dict[str, Any]: ...\n    def queue(');out[str(f)]=s
f=p/"infrastructure/interwarehouse.py";s=f.read_text(encoding="utf-8")
s=s.replace('        try:\n            return self.posting.post(StockCommand(operation_id=operation_id,command_type=kind', '''        metadata = dict(metadata)
        scans = metadata.pop("scans",None)
        if scans:
            from ..domain.mark_identity import canonical_mark
            from fastapi import HTTPException
            try:
                metadata["unit_scans"] = [{"system_code":x["system_code"],"profile_code":x["profile_code"],
                    "code_hash":sha256(canonical_mark(x["system_code"],x["profile_code"],x["code"])["identity"].encode("utf-8")).hexdigest()} for x in scans]
            except ValueError as exc:
                raise HTTPException(422,str(exc)) from exc
        try:
            return self.posting.post(StockCommand(operation_id=operation_id,command_type=kind''')
s=s.replace('    def queue(','''    def unit_manifest(self, plan_id: str, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Current scoped interwarehouse unit source") as q:
                q.execute("set transaction read only")
                q.execute("select RRL_INTERWARE_UNIT_SOURCE.plan_manifest(:plan,:actor) from dual",plan=plan_id,actor=actor)
                result = read_oracle_json(q.fetchone()[0])
                q.execute("select p.SYSTEM_CODE,p.PROFILE_CODE,p.PROFILE_VERSION,p.SCAN_MODE from RRL_SKU_RECEIPT_PROFILE p join RRL_PALLETS l on l.ARTICUL=p.ARTICUL join RRL_INTERWARE_PLAN i on i.ROOT_UID=l.UID_PALLET where i.OPERATION_ID=:plan order by p.SYSTEM_CODE,p.PROFILE_CODE fetch first 51 rows only",plan=plan_id)
                result["profiles"] = [{"system_code":r[0],"profile_code":r[1],"profile_version":r[2],"scan_mode":r[3]} for r in q.fetchall()]
                return result
        except oracledb.DatabaseError as exc:
            code = getattr(exc.args[0],"code",0)
            raise StoreReturnReceiveError("INTERWARE_MANIFEST_REJECTED",str(exc.args[0]).split("\\n",1)[0],403 if code==20882 else 409) from exc

    def queue(''')
out[str(f)]=s
print(json.dumps(out,ensure_ascii=True))
