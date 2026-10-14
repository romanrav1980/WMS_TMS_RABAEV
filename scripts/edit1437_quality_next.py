from pathlib import Path
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/quality_transport_read.py');p.write_text('''"""Existing ST assignment for navigation from the current QC snapshot."""
from typing import Any


def quality_transport_read(cur: Any, identifier: str, actor: str) -> dict[str, Any]:
    cur.execute("""select s.ID,s.TRANSTASK_ID from RRL_SBORKA_PALLETS s
        where s.PALLET_UID=:identifier
        and RRL_HAS_WRIGHT(:actor,'transport_dispatch_view')=1
        order by s.ID fetch first 2 rows only""", identifier=identifier, actor=actor)
    rows = cur.fetchall()
    if len(rows) != 1:
        return {"state": "UNAVAILABLE"}
    row = rows[0]
    return {"state": "ASSIGNED" if row[1] is not None else "UNASSIGNED",
            "shipment_id": int(row[0]), "transport_task_id": int(row[1]) if row[1] is not None else None}
''',encoding='utf-8')
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py');s=p.read_text(encoding='utf-8').replace('                    result = read_oracle_json(q.fetchone()[0])','                    result = read_oracle_json(q.fetchone()[0])\n                    from .quality_transport_read import quality_transport_read\n                    result["transport_assignment"] = quality_transport_read(q, canonical, actor)');p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/outgoing-quality-next.js');p.write_text('''/* Navigation uses current server assignment; it never grants physical admission. */
(() => {
 let panel;
 function render(parent,snapshot,blocked){
  if(!panel){panel=document.createElement('div');panel.className='qc-actions';parent.querySelector('.qc-toolbar').after(panel);}
  panel.replaceChildren();panel.hidden=true;
  if(!snapshot||blocked||!window.wmsAdminAuth.hasPermission('transport_dispatch_view'))return;
  panel.hidden=false;
  const note=document.createElement('span');
  if(snapshot.ready!==true&&snapshot.required!==false){note.textContent='До погрузки требуется допуск текущего состава.';panel.append(note);return;}
  const assignment=snapshot.transport_assignment;
  if(assignment?.state!=='ASSIGNED'||!Number.isSafeInteger(assignment.transport_task_id)||assignment.transport_task_id<1){
   note.textContent=assignment?.state==='UNASSIGNED'?'Для СТ ещё не назначен рейс. Назначьте его в существующем диспетчере.':'Назначение рейса недоступно; перечитайте СТ после назначения в диспетчере.';panel.append(note);return;
  }
  const a=document.createElement('a');a.textContent='Открыть погрузку рейса '+assignment.transport_task_id;
  a.href='transport-loading.html?trip_id='+assignment.transport_task_id;
  a.title='Показать текущее назначение и факты рейса. Допуск состава и физические сканы проверяются отдельно при погрузке.';
  panel.append(a);
 }
 window.wmsQualityNext={render};
})();
''',encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/outgoing-quality.js');s=p.read_text(encoding='utf-8');s=s.replace(' function controls(){',' function controls(){\n  window.wmsQualityNext.render(panel,snapshot,busy||!!pending||damaged());');p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.html');s=p.read_text(encoding='utf-8').replace('<script src="outgoing-quality.js?v=20261013-1130"></script>', '<script src="outgoing-quality-next.js"></script><script src="outgoing-quality.js?v=20261014-1437"></script>');p.write_text(s,encoding='utf-8')
