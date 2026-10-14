from pathlib import Path
import json
p=Path("admin/wms_admin_frontend/src/components/TransportGanttPage.tsx");s=p.read_text(encoding="utf-8").replace('import { TransportTimePreflight } from "./TransportTimePreflight";\n\n','import { TransportTimePreflight } from "./TransportTimePreflight";\n')
s=s.replace('            <div className="gantt-card-actions">\n              <TransportTimePreflight key={taskCard.tt_id} tripId={taskCard.tt_id}\n                apiBase={API_BASE} headers={apiHeaders()} />','            <div className="gantt-card-actions"><TransportTimePreflight key={taskCard.tt_id} tripId={taskCard.tt_id} apiBase={API_BASE} headers={apiHeaders()} />')
q=Path("scripts/inspect247.py")
print(json.dumps({str(p):s,str(q):q.read_text(encoding="utf-8").replace("between33529 and33531","between 33529 and 33531")},ensure_ascii=True))
