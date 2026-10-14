from pathlib import Path
import json
out={}
p=Path("wiki/index.md");out[str(p)]="- [NI07.2 waiting tasks772: контракт перед применением](database/retailcase_ni072_waiting_tasks_20261013.md): typed existing TASK_COMPLETE/TRANSFER_CORE, immutable origin, no second stock writer; actual evidence pending.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 checkpoint772 before apply: captured771 current native packages/SHA, additive waiting-run/plan and typed existing task handlers. Dev authorization already given; paired rollback preserves history/no active tasks. Actual case/compilation pending.\n"
print(json.dumps(out,ensure_ascii=True))
