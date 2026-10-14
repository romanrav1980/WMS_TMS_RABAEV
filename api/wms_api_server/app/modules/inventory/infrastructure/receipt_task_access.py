"""Current native task scope shared with normal assignment and physical posting."""
import oracledb

def assert_receipt_task_scope(cursor: oracledb.Cursor,task_id: int,actor: str) -> None:
    try:
        cursor.execute("begin RRL_WAREHOUSE_TASK_ACCESS.assert_scope(:task,:actor);end;",
                       {"task":task_id,"actor":actor})
    except oracledb.DatabaseError as exc:
        if getattr(exc.args[0],"code",None)==20882:
            raise PermissionError("TASK_USER_WAREHOUSE_FORBIDDEN") from exc
        raise
