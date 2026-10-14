from pathlib import Path
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/task_read_scope.py");s=p.read_text(encoding="utf-8")
s+='''

def read_task_progress_snapshot(gateway: OracleGateway,task_id: int,actor: str) -> dict:
    from .task_progress import task_progress
    def load(bound: TransactionGateway,scope: TaskViewScope) -> dict:
        result=task_progress(bound,task_id)
        if not scope.global_admin:
            for row in result["tasks"]:
                try:
                    bound.cursor.callproc("RRL_WAREHOUSE_TASK_ACCESS.assert_scope",[row["task_id"],actor,None])
                except oracledb.DatabaseError as exc:
                    if getattr(exc.args[0],"code",None)==20882:
                        raise TaskReadError("TASK_FAMILY_WAREHOUSE_FORBIDDEN") from exc
                    raise
        return result
    return read_task_snapshot(gateway,actor,load,task_id)
''';p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8").replace("from .infrastructure.task_read_scope import read_task_snapshot","from .infrastructure.task_read_scope import read_task_snapshot,read_task_progress_snapshot",1).replace('"TaskViewScope","read_task_snapshot"]','"TaskViewScope","read_task_snapshot","read_task_progress_snapshot"]',1);p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/routers/warehouse_tasks.py");s=p.read_text(encoding="utf-8").replace("TaskViewScope,read_task_snapshot","TaskViewScope,read_task_snapshot,read_task_progress_snapshot",1)
s=s.replace("    from ..modules.inventory.public import get_existing_task_progress\n    return _read(_user,lambda gateway,scope: get_existing_task_progress(gateway,task_id),task_id)","""    try:
        return read_task_progress_snapshot(WarehouseTaskService().gateway,task_id,_user.username)
    except TaskReadError as exc:
        raise HTTPException(exc.status,detail=exc.code) from exc""",1);p.write_text(s,encoding="utf-8")
