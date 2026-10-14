from pathlib import Path
import json
files={}
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.html")
s=p.read_text(encoding="utf-8")
s=s.replace('              <button id="warehouseTaskAssign"', '              <div class="warehouse-task-command-row"><button id="warehouseTaskAssign"',1)
s=s.replace('              <button id="warehouseTaskComplete" type="button">Завершить</button>','              <button id="warehouseTaskComplete" type="button">Завершить</button></div>',1)
s=s.replace('20261013-821','20261013-829')
s=s.replace('warehouse-tasks.css?v=20261013-802','warehouse-tasks.css?v=20261013-829')
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.css")
files[str(p)]=p.read_text(encoding="utf-8")+"""
.warehouse-operations .warehouse-task-execute{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));align-items:end}
.warehouse-operations .warehouse-task-execute label{min-width:0;display:flex;flex-direction:column;gap:6px;white-space:normal}
.warehouse-operations .warehouse-task-execute input{width:100%;min-width:0;box-sizing:border-box}
.warehouse-operations .warehouse-task-command-row{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:10px;padding-top:6px}
.warehouse-operations .warehouse-task-command-row button{min-width:120px;padding:8px 18px}
@media(max-width:650px){.warehouse-operations .warehouse-task-execute{grid-template-columns:1fr}.warehouse-operations .warehouse-task-command-row button{flex:1}}
"""
p=Path("wiki/components/nicora_warehouse_task_ui_20261013.md")
files[str(p)]=p.read_text(encoding="utf-8")+"""
## Продолжение827–829

После перечитывания выбранная карточка заменяется свежей записью очереди: прежний статус больше не сохраняется. Запоздавший ответ progress отвергается по readEpoch и actor/API. JS828 подтвердил ASSIGNED→DONE/disabled и старый progress без записи Oracle. Подтверждённое назначение ресурса показывается после обновления; ошибка обновления отдельно сообщает о сохранённом назначении и не предлагает дублировать его. Новый фактический dispatch не выполнялся.

В браузере создана новая вкладка734: собственный dev admin, прямое чтение1080 DONE/3EA/remaining0. Preset снова не изменил список через CUA; причина открыта. Скриншот07 показывает действительную карточку, но обнаружил тесную сетку полей.829 разносит поля сканирования и ряд команд; visual after-change pending. SQL: актуальный LIST15.701мс/95buffers, retain bounded projection без нового индекса. До20:00 MSK13Oct либо полного завершения по новому поручению.
"""
p=Path("wiki/index.md")
files[str(p)]="- [Продолжение827–829: актуальная карточка заданий](components/nicora_warehouse_task_ui_20261013.md): fresh status/progress guard, JS828 PASS, scan layout; дедлайн20:00 MSK.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md")
files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 continuation827–829: owner deadline20:00MSK persisted; current card fresh list status + progress epoch/identity, resource confirmed result after queue read; JS828/810PASS. Real browser7341080DONE/3EA0 screenshot07, preset remains unconfirmed. Scan grid829 fixes crowded labels; visual pending. LIST15.701ms95buf bounded retained.\n"
print(json.dumps(files,ensure_ascii=True))
