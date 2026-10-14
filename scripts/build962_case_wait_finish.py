from pathlib import Path
import json
old=Path("scripts/resume956_case_wait.py").read_text(encoding="utf-8")
head=old[:old.index(' q.execute("select PICK_WAVE_ID from RRL_PICK_WAVE')]
head=head.replace('assert context["stage"]=="NEW","Use a separate phase continuation for a progressed source"','assert context["stage"]=="DEFERRED","Use current phase only; no source rebirth"')
head+=' wave=context["wave"];revision=context["revision"];wait=context["wait"];ct=context["case"];carrier=context["carrier"];decision=context["decision"]\n'
head+=' q.execute("select PICK_PLAN_ID from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=:w",w=wave);plans=[int(r[0])for r in q.fetchall()]\n'
head+=' from app.modules.platform.public import read_oracle_json\n from app.modules.inventory.infrastructure.task_completion import complete_existing_task\n from app.schemas import WarehouseTaskStatusRequest\n try:\n'
tail=old[old.index("  def planning():"):]
print(json.dumps({"scripts/finish962_case_wait.py":head+tail},ensure_ascii=True))
