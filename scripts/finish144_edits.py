from pathlib import Path
import json
out={}
p=Path("scripts/build144.py");out[str(p)]=p.read_text(encoding="utf-8").replace("select WARE,USER_GROUP","select WARE_ID,USER_GROUP")
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/task_completion.py")
text=p.read_text(encoding="utf-8").replace("from fastapi import HTTPException","from fastapi import HTTPException\nimport oracledb")
old='''            cursor.execute(
                "begin RRL_WAREHOUSE_TASK_ACCESS.assert_scope(:task,:actor,:assignee);end;",
                {"task": task_id, "actor": request.updated_by,
                 "assignee": request.assigned_to if action == "assign_task" else None},
            )'''
new='''            try:
                cursor.execute(
                    "begin RRL_WAREHOUSE_TASK_ACCESS.assert_scope(:task,:actor,:assignee);end;",
                    {"task": task_id, "actor": request.updated_by,
                     "assignee": request.assigned_to if action == "assign_task" else None},
                )
            except oracledb.DatabaseError as exc:
                if getattr(exc.args[0], "code", None) == 20882:
                    raise HTTPException(403, detail="TASK_USER_WAREHOUSE_FORBIDDEN") from exc
                raise'''
assert old in text
out[str(p)]=text.replace(old,new)
print(json.dumps(out,ensure_ascii=True))
