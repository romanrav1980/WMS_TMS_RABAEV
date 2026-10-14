from pathlib import Path
p=Path(__file__).resolve().parents[1]/"api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py"
s=p.read_text(encoding="utf-8").replace('from typing import Any\n','from typing import Any\nimport oracledb\n',1)
a=s.index('def task_scope(');b=s.index('\n\nclass ScopedCaseReads',a)
s=s[:a]+'''def task_scope(cur: Any, task: int, actor: str) -> None:
    actor_scope(cur, actor)
    try:
        cur.callproc("RRL_CASE_TASK_ACCESS.assert_scope", [task, actor, "case_pick_view", None])
    except oracledb.DatabaseError as exc:
        code = getattr(exc.args[0], "code", 0)
        if code == 20882:
            raise CaseReadError("CASE_CURRENT_WARE_VIEWER_REQUIRED", "Недоступный склад CASE-задания") from exc
        if code == 20886:
            missing = "CASE_TASK_IDENTITY_MISSING" in str(exc.args[0])
            raise CaseReadError("CASE_TASK_NOT_FOUND" if missing else "CASE_TASK_WARE_REQUIRED",
                                "CASE-задание отсутствует" if missing else "Не задан склад CASE-задания",
                                404 if missing else 409) from exc
        raise
'''+s[b:]
p.write_text(s,encoding="utf-8")
