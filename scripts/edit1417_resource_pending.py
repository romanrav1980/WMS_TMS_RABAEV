from pathlib import Path
p=Path('wiki-raw/wms_admin_ui_reference/resource-workload.html');s=p.read_text(encoding='utf-8').replace('<script src="resource-workload.js">','<script src="wave-command-intent.js"></script><script src="resource-pending.js"></script><script src="resource-workload.js">');p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/resource-workload.js');s=p.read_text(encoding='utf-8');a=s.index('  function pending()');b=s.index('  function reset()',a);s=s[:a]+'''  const intent=window.wmsResourcePending.create(pendingKey,'workload','rwRetry',async()=>{reset();await refresh();message('Исходник архивирован. Сверьте текущее состояние перед новой командой.');});
  function pending() { const r=intent.read(); return r.damaged?{damaged:true}:r.value; }
'''+s[b:];s=s.replace('error.status = response.status; throw error;', 'error.status = response.status; error.code=result.detail?.code; throw error;')
s=s.replace('    localStorage.setItem(pendingKey(), JSON.stringify(saved)); el("rwRetry").hidden = false;', '    intent.save(saved); el("rwRetry").hidden = false;')
a=s.index('  async function retryUnlocked()');b=s.index('  function localSecond',a)
s=s[:a]+'''  async function retryUnlocked() {
    const record=intent.read(),saved=record.value;
    if(record.damaged)throw Error('Запрос повреждён. Сначала сохраните его в архив и перечитайте настройки.');
    if(!saved)return;
    const identity=owner(); el("rwRetry").disabled=true;
    try {
      const result=await request(saved.path,"POST",saved.body);
      if(identity!==owner())return;
      if(!intent.confirms(saved,result))throw Error('Ответ не подтверждает исходную операцию. Повторите сохранённый запрос.');
      intent.settle(record);el("rwRetry").hidden=true;await refresh();message('Действие подтверждено: '+result.operation_id);
    } catch(error) {
      if(identity!==owner())return;
      if(intent.rejected(error))intent.settle(record);
      message(error.message+(intent.read().raw!==null?' Повторите исходное действие.':' Исправьте данные после перечитывания настроек.'));
      el("rwRetry").hidden=!pending();
    } finally {if(identity===owner())el("rwRetry").disabled=false;}
  }
'''+s[b:];p.write_text(s,encoding='utf-8')
