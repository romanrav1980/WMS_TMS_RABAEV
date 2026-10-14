from pathlib import Path
import json
files={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/fullpal_shipment.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ..contracts_stock import StockCommand","from ..contracts_stock import StockCommand, StockPostingError")
s=s.replace("def preview(self, task_id: int) -> dict:", "def preview(self, task_id: int, actor: str | None = None) -> dict:")
point='        rows = self.gateway.fetch_all("""'
assert point in s
s=s.replace(point,'''        if actor is not None:
            self.gateway.execute_plsql("begin RRL_WAREHOUSE_TASK_ACCESS.assert_scope(:task,:actor);end;",
                                       {"task": task_id, "actor": actor})
        rows = self.gateway.fetch_all("""''',1)
files[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py");s=p.read_text(encoding="utf-8")
s="import oracledb\n"+s
s=s.replace("def preview(self, task_id: int) -> dict: ...","def preview(self, task_id: int, actor: str | None = None) -> dict: ...")
s=s.replace("return service.preview(task_id)","return service.preview(task_id, _user.username)")
point='    except ValueError as exc:\n        raise HTTPException(409, str(exc)) from exc'
assert point in s
s=s.replace(point,point+'''
    except oracledb.Error as exc:
        if getattr(exc.args[0], "code", None) == 20882:
            raise HTTPException(403, "TASK_CURRENT_WAREHOUSE_REQUIRED") from exc
        raise''',1)
s=s.replace('"code":exc.code,"operation_id":exc.operation_id,"outcome_confirmed":not uncertain,','"code":exc.code,"message":exc.rule_reason,"operation_id":exc.operation_id,"outcome_confirmed":not uncertain,')
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.css")
files[str(p)]=p.read_text(encoding="utf-8")+"""
.fullpal-shipment-panel{padding:24px;margin:20px 0;border-radius:16px}
.fullpal-shipment-panel p{line-height:1.6}
.fullpal-shipment-panel .fullpal-fields{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,2fr) minmax(0,2fr);gap:12px;align-items:end;margin:16px 0}
.fullpal-shipment-panel label{display:grid;gap:8px;color:#475569;font-size:13px}
.fullpal-shipment-panel input,.fullpal-shipment-panel button,.fullpal-shipment-panel .fullpal-actions a{min-height:44px;border-radius:9px;padding:10px 14px;box-sizing:border-box;border:1px solid #cad6e5}
.fullpal-shipment-panel input{width:100%;min-width:0}
.fullpal-shipment-panel [data-bind]{background:#2377eb;color:white}
.fullpal-shipment-panel .fullpal-actions{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}
.fullpal-shipment-panel [role=status],.fullpal-shipment-panel [data-fact]{background:#eff6ff;padding:12px;border-radius:10px}
.fullpal-shipment-panel [hidden]{display:none!important}
.fullpal-shipment-panel button:disabled{opacity:.5}
@media(max-width:800px){.fullpal-shipment-panel .fullpal-fields{grid-template-columns:minmax(0,1fr)}}
"""
print(json.dumps(files))
