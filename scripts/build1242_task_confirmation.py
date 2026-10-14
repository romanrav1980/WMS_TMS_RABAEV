from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.js");s=p.read_text(encoding="utf-8")
a='''      await loadWarehouseTasks();
      if (result.residual_task_id) selectWarehouseTask(result.residual_task_id);'''
b='''      warehouseTaskState.initialTaskId=result.residual_task_id||event.detail.task_id;
      await loadWarehouseTasks();'''
assert s.count(a)==1;s=s.replace(a,b);out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-task-recovery.js");s=p.read_text(encoding="utf-8")
s=s.replace('''    busy = true; render();
    try {''','''    const storageKey=key(saved.task_id),raw=localStorage.getItem(storageKey);
    if(raw!==JSON.stringify(saved))throw new Error("Сохранённая команда изменилась. Перечитайте задание.");
    const current=()=>key(saved.task_id)===storageKey&&localStorage.getItem(storageKey)===raw;
    busy = true; render();
    try {''',1)
a='''      localStorage.removeItem(key(saved.task_id));
      window.dispatchEvent(new CustomEvent("warehouse-task-confirmed",
        {detail: {task_id: saved.task_id, result: response.result || response}}));'''
b='''      const result=response.result||response;
      if(result.task_id!==saved.task_id||result.operation_id!==saved.payload.operation_id)
        throw new Error("Ответ не подтверждает исходное задание и операцию. Повторите сохранённую команду.");
      if(!current())throw new Error("Пользователь или сохранённая команда изменились. Результат перечитывается в исходной сессии.");
      localStorage.removeItem(storageKey);
      window.dispatchEvent(new CustomEvent("warehouse-task-confirmed",
        {detail: {task_id: saved.task_id, result}}));'''
assert s.count(a)==1;s=s.replace(a,b)
s=s.replace('''      if ([400, 422].includes(error.status) ||
          (error.code === "STOCK_RULE_REJECTED" && [20881, 20886, 20887].includes(error.oracleCode))) {
        localStorage.removeItem(key(saved.task_id));''','''      if (current()&&([400, 422].includes(error.status) ||
          (error.code === "STOCK_RULE_REJECTED" && [20881, 20886, 20887].includes(error.oracleCode)))) {
        localStorage.removeItem(storageKey);''')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/receiving.js");s=p.read_text(encoding="utf-8")
s=s.replace('''    const data=await response.json();''','''    const responseText=await response.text();
    let data;
    try{data=JSON.parse(responseText);}catch{
      throw new Error(body?'Сервер не подтвердил результат. Исходная команда сохранена; повторите её без изменения данных.':'Сервер не вернул данные. Повторите чтение.');
    }''',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
