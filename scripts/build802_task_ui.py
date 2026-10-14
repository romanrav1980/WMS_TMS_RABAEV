from pathlib import Path
import json
files={}
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.html");t=p.read_text(encoding="utf-8")
t=t.replace('</head>','<link rel="stylesheet" href="warehouse-tasks.css?v=20261013" />\n  </head>')
t=t.replace('body class="auth-pending"','body class="auth-pending warehouse-operations"')
t=t.replace('<button class="round alert">12</button>','').replace('<button class="round">?</button>','')
t=t.replace('<kbd>Ctrl K</kbd>','')
t=t.replace('Паллет, SSCC, ячейка, исполнитель...','Идентификатор паллеты, ячейка, исполнитель...')
t=t.replace('<div class="footer-line"><span>Смена</span><b>1 смена</b></div>','<div class="footer-line"><span>RETAILCASE</span><b>Складские задания</b></div>')
t=t.replace('<div class="footer-line muted"><span>18.05.2026</span><span>10:24</span></div>','')
t=t.replace('<div class="footer-line muted"><span>Версия</span><span>2.4.1</span></div>','')
t=t.replace('<option value="PUTAWAY">Размещение приёмки</option>','<option value="PUTAWAY">Размещение / ожидание</option>')
t=t.replace('<label>Документ<input','<label>Тип документа<select id="warehouseTaskDocType" title="Ограничить очередь по происхождению задания"><option value="">Все</option><option value="ST_DEFER">Перенос СТ</option><option value="SHIPMENT">Отгрузка</option><option value="PICK_WAVE">Волна отбора</option></select></label>\n              <label>Документ<input')
t=t.replace('<button type="button" data-task-preset="all" class="active">Все</button>','<button type="button" data-task-preset="all" class="active">Все</button>\n              <button type="button" data-task-preset="waiting" title="Показать штатные задания ожидания после переноса СТ">Ожидание рейса</button>')
t=t.replace('<th>Паллет</th>','<th>Идентификатор паллеты</th>').replace('<dt>Паллет</dt>','<dt>Идентификатор паллеты</dt>').replace('Скан паллета','Скан идентификатора паллеты')
t=t.replace('<header><h2>Исполнение</h2></header>','<header><h2>Карточка задания</h2></header>')
files[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.js");t=p.read_text(encoding="utf-8")
t=t.replace('if (sourceDoc) params.set("source_doc_id", sourceDoc);','if (sourceDoc) params.set("source_doc_id", sourceDoc);\n  const docType=warehouseTaskEl("warehouseTaskDocType").value;\n  if(docType)params.set("source_doc_type",docType);')
t=t.replace('if (preset === "wave-pickface") {','warehouseTaskEl("warehouseTaskDocType").value = "";\n  if (preset === "waiting") {\n    warehouseTaskEl("warehouseTaskType").value = "PUTAWAY";\n    warehouseTaskEl("warehouseTaskSource").value = "MANUAL";\n    warehouseTaskEl("warehouseTaskDocType").value = "ST_DEFER";\n  } else if (preset === "wave-pickface") {')
t=t.replace('TASK_TYPE_LABELS[task.task_type] || task.task_type)}</b>', 'classifyTask(task))}</b>')
# Keep source/task labels in detail consistent.
t=t.replace('TASK_TYPE_LABELS[task.task_type] || task.task_type}', 'classifyTask(task)}')
files[str(p)]=t
print(json.dumps(files,ensure_ascii=True))
