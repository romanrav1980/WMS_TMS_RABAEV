import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/delivery/contracts.py");v=p.read_text(encoding="utf-8");a=v.index("    def release_custody(")
v=v[:a]+'''    def start_unloading(self,body: dict[str,Any],actor: str)->dict[str,Any]: ...
    def unloading(self,load: str,address: str,actor: str)->dict[str,Any]: ...
'''+v[a:];out[str(p)]=v
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py");v=p.read_text(encoding="utf-8");a=v.index("    def release_custody(")
v=v[:a]+'''    def start_unloading(self,body: dict[str,Any],actor: str)->dict[str,Any]:
        from .store_unloading import start_unloading
        return start_unloading(self.gateway,body,actor)

    def unloading(self,load: str,address: str,actor: str)->dict[str,Any]:
        from .store_unloading import read_unloading
        return read_unloading(self.gateway,load,address,actor)

'''+v[a:]
v=v.replace("        metadata=dict(metadata)","        metadata=dict(metadata)\n        if metadata.get('unloading')is None:metadata.pop('unloading',None)",1)
out[str(p)]=v
p=Path("api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py");v=p.read_text(encoding="utf-8");a=v.index("class StoreReceiptRequest")
v=v[:a]+'''class UnloadingDetails(BaseModel):
    model_config=ConfigDict(extra="forbid")
    start_operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    method: Literal["ROLL_CAGE","PALLET","MANUAL"]
    rolling_difficult: bool=Field(strict=True)
    loader_present: bool=Field(strict=True)
    evidence_reference: str=Field(strict=True,min_length=1,max_length=100)


class UnloadingStart(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    load_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    store_address: str=Field(strict=True,min_length=1,max_length=255)
    expected_composition_signature: str=Field(strict=True,pattern=r"^[A-F0-9]{64}$")
    scan_place: str=Field(strict=True,min_length=1,max_length=200)
    before_cameras: bool=Field(strict=True)


'''+v[a:]
v=v.replace("class StoreReceiptRequest(BaseModel):","class StoreReceiptRequest(BaseModel):\n    unloading: UnloadingDetails|None=None")
v=v.replace('metadata=body.model_dump(exclude={','metadata=body.model_dump(exclude_none=True,exclude={',1)
v+='''\n@router.post("/unloading/start")
def start_unloading(body: UnloadingStart,user: AdminUser=Depends(require_permission("store_receipt_confirm")),
                    service: StoreReceiptPort=Depends(store_receipt_service))->dict[str,Any]:
    try:return service.start_unloading(body.model_dump(mode="json"),user.username)
    except StoreReceiptError as exc:raise failure(exc)from exc


@router.get("/unloading")
def unloading(load_operation_id: str,store_address: str,
              user: AdminUser=Depends(require_permission("store_receipt_confirm")),
              service: StoreReceiptPort=Depends(store_receipt_service))->dict[str,Any]:
    try:return service.unloading(load_operation_id,store_address,user.username)
    except StoreReceiptError as exc:raise failure(exc)from exc
'''
out[str(p)]=v
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_receipt_read.py");v=p.read_text(encoding="utf-8")
v=v.replace("from ..contracts import StoreReceiptError","from ..contracts import StoreReceiptError\nfrom ...platform.public import read_oracle_json\nfrom .store_unloading import unloading_fact")
a=v.index('        rows=gateway.fetch_all(');b=v.index('    except oracledb.DatabaseError',a)
v=v[:a]+'''        with gateway.transaction("Read receipt and unloading in one snapshot")as cursor:
            cursor.execute("set transaction read only")
            cursor.execute("select RRL_STOCK_STORE_RECEIPT_READ.preview_json(:op,:actor,:addr)from dual",
                           op=load_operation_id,actor=actor,addr=store_address)
            result=read_oracle_json(cursor.fetchone()[0])
            return {**result,"unloading":unloading_fact(cursor,load_operation_id,store_address)}
'''+v[b:]
a=v.index('    value=rows[0]');v=v[:a]
v=v.replace("import json\n","");out[str(p)]=v
print(json.dumps(out))
