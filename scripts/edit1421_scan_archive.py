from pathlib import Path
p=Path('wiki-raw/wms_admin_ui_reference/warehouse-task-scans.js');s=p.read_text(encoding='utf-8').replace('<p role="status"></p><pre></pre>', '<button data-action="archive" hidden>Архивировать повреждённый запрос</button><p role="status"></p><pre></pre>')
s=s.replace("    panel.hidden=!auth()?.hasPermission('warehouse_task_execute');", """    panel.hidden=!auth()?.hasPermission('warehouse_task_execute');
    const repair=panel.querySelector('[data-action="archive"]');repair.hidden=true;
    if(task()&&auth()?.state.user){try{
      const raw=localStorage.getItem('wms.task.scans:'+auth().state.apiBase+':'+auth().state.user.username+':'+task());
      if(raw!==null){try{repair.hidden=validBody(JSON.parse(raw));}catch{repair.hidden=false;}}
    }catch{message('Хранилище недоступно. Отправка требует сохранённого исходного запроса.');}}
""")
anchor='  async function run(action){'
s=s.replace(anchor,"""  async function archive(s){
    const raw=localStorage.getItem(s.key);if(raw===null)throw Error('Повреждённый запрос не найден.');
    let valid=false;try{valid=validBody(JSON.parse(raw));}catch{}
    if(valid)throw Error('Запрос имеет правильный формат. Повторите его без изменения идентификатора.');
    const archived=s.key+':damaged:'+crypto.randomUUID();localStorage.setItem(archived,raw);
    if(localStorage.getItem(archived)!==raw||localStorage.getItem(s.key)!==raw)throw Error('Архив не подтверждён или исходник изменён.');
    localStorage.removeItem(s.key);if(localStorage.getItem(s.key)!==null)throw Error('Архив сохранён, но исходник не освобождён.');
    await load(s);if(active(s))message('Исходник сохранён в архиве. Показан текущий серверный набор; товарное движение не выполнялось.');
  }
"""+anchor)
s=s.replace("      if(action==='load')await load(s);", "      if(action==='load')await load(s);\n      if(action==='archive')await archive(s);")
p.write_text(s,encoding='utf-8')
