from pathlib import Path
import json
files={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/fullpal_shipment.py");s=p.read_text(encoding="utf-8")
s=s.replace("from __future__ import annotations","from __future__ import annotations\nimport oracledb",1)
old='''            self.gateway.execute_plsql("begin RRL_WAREHOUSE_TASK_ACCESS.assert_scope(:task,:actor);end;",
                                       {"task": task_id, "actor": actor})'''
new='''            try:
                self.gateway.execute_plsql("begin RRL_WAREHOUSE_TASK_ACCESS.assert_scope(:task,:actor);end;",
                                           {"task": task_id, "actor": actor})
            except oracledb.Error as exc:
                if getattr(exc.args[0], "code", None) == 20882:
                    raise StockPostingError("TASK_CURRENT_WAREHOUSE_REQUIRED", "READ", 20882) from exc
                raise'''
assert old in s;files[str(p)]=s.replace(old,new)
p=Path("api/wms_api_server/app/modules/inventory/api/fullpal_shipment_routes.py");s=p.read_text(encoding="utf-8")
s=s.removeprefix("import oracledb\n")
old='''    except oracledb.Error as exc:
        if getattr(exc.args[0], "code", None) == 20882:
            raise HTTPException(403, "TASK_CURRENT_WAREHOUSE_REQUIRED") from exc
        raise'''
assert old in s;s=s.replace(old,'''    except StockPostingError as exc:
        raise HTTPException(403 if exc.oracle_code == 20882 else 409, detail={"code": exc.code}) from exc''')
files[str(p)]=s
print(json.dumps(files))
