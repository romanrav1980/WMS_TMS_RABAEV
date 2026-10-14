from pathlib import Path
p=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.js')
s=p.read_text(encoding='utf-8')
a=s.index('  for(const id of ["warehouseTaskAssign"')
b=s.index('  warehouseTaskEl("warehouseTaskSelectionText")',a)
s=s[:a]+'  window.warehouseTaskActions.render(task);\n'+s[b:]
s=s.replace('  } else {\n    await warehouseTaskFetch(`/api/warehouse-tasks/${task.task_id}/${action}`, {','  } else {\n    await window.warehouseTaskActions.send(task, action, payload);\n    return;\n  }\n}\n\nasync function unusedWarehouseTaskAction() {\n    await warehouseTaskFetch(`/api/warehouse-tasks/${task.task_id}/${action}`, {') if False else s
start=s.index('  } else {\n    await warehouseTaskFetch(`/api/warehouse-tasks/${task.task_id}/${action}`')
end=s.index('\nfunction classifyTask',start)
s=s[:start]+'''  } else {
    await window.warehouseTaskActions.send(task, action, payload);
  }
}
''' + s[end:]
p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.html');s=p.read_text(encoding='utf-8').replace('<script src="warehouse-task-family.js">','<script src="warehouse-task-actions.js"></script><script src="warehouse-task-family.js">').replace('<div class="rights-summary"><span id="warehouseTaskDetailStatus">','<p id="warehouseTaskActionHint" class="subtle" role="status"></p>\n            <div class="rights-summary"><span id="warehouseTaskDetailStatus">').replace('id="warehouseTaskEditAssignee" placeholder="driver"','id="warehouseTaskEditAssignee" placeholder="driver" title="Кому назначить задание до начала исполнения. Начать может текущий вошедший пользователь."').replace('id="warehouseTaskAssign" type="button">Взять','id="warehouseTaskAssign" type="button">Назначить');p.write_text(s,encoding='utf-8')
