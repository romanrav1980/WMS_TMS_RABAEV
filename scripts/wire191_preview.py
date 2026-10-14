from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni042_order_weight_policy")
p=f/"002_preview.sql";t=p.read_text(encoding="utf-8").replace("   actual:=actual+to_number(row_json.get_string('picked_quantity'),'999999999999999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''');","   if row_json.get_string('picked_quantity')!='0'then actual:=actual+RRL_STOCK_MATH.quantity(row_json.get_string('picked_quantity'));end if;")
out[str(p)]=t
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@002_preview.sql\n"
out[str(f/"rollback.sql")]="drop package RRL_ORDER_WEIGHT_READ;\n"+(f/"rollback.sql").read_text(encoding="utf-8")
out[str(f/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-11-191-order-weight-policy","sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in f.glob("*.sql")},"recovery":"Additive default15 metadata/empty read helper; preserve configured changes with forward repair; existing source/checkpoint; no DB copy"},indent=2)
p=Path("api/wms_api_server/app/modules/inventory/contracts_weighted_case.py");t=p.read_text(encoding="utf-8").replace("class WeightedCasePort(Protocol):","class WeightedCasePort(Protocol):\n    def weight_preview(self, task: int, line: int, actor: str) -> dict[str, Any]: ...")
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py");t=p.read_text(encoding="utf-8")
a="    def weigh_line(self,"
t=t.replace(a,'''    def weight_preview(self, task: int, line: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Order SKU weight admission READ ONLY") as q:
                q.execute("set transaction read only")
                return read_oracle_json(q.callfunc("RRL_ORDER_WEIGHT_READ.snapshot_json", oracledb.DB_TYPE_CLOB, [task, line, actor]))
        except oracledb.DatabaseError as exc:
            code = exc.args[0].code
            if code in {20882, 20886, 20881, 1403, 1422}:
                raise StockPostingError("ORDER_WEIGHT_PREVIEW_REJECTED", None, code) from exc
            raise

'''+a)
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py");t=p.read_text(encoding="utf-8")
t+='''

@router.get("/tasks/{task}/lines/{line}/order-weight-preview")
def order_weight_preview(task: int, line: int,
                         user: AdminUser = Depends(require_permission("case_pick_execute")),
                         service: WeightedCasePort = Depends(weighted_case_service)) -> dict:
    return service.weight_preview(task, line, user.username)
'''
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
