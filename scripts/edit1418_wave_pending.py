from pathlib import Path
p=Path('wiki-raw/wms_admin_ui_reference/resource-workload.js');s=p.read_text(encoding='utf-8').replace('function pending() { const r=intent.read();','function pending() { if(!auth().state.user)return null; const r=intent.read();');p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/resource-wave-time.js');s=p.read_text(encoding='utf-8').replace('let context = null, sequence = 0, currentOwner = "";','let context = null, sequence = 0, currentOwner = "", busy=false;')
a=s.index('  const pending =');b=s.index('  function reset()',a)
s=s[:a]+'''  const intent=window.wmsResourcePending.create(key,'wave','wtRetry',async()=>{reset();await load();message('Исходник архивирован. Сверьте утверждённое окно перед новой командой.');});
  const pending=()=>{if(!auth().state.user)return null;const r=intent.read();return r.damaged?{damaged:true}:r.value;};
'''+s[b:];s=s.replace('error.status = response.status; throw error;', 'error.status = response.status; error.code=result.detail?.code; throw error;')
s=s.replace('  async function approve() {\n    try {','  async function approve() {\n    if(busy)return;\n    try {');s=s.replace('      localStorage.setItem(key(), JSON.stringify(saved)); el("wtRetry").hidden = false;','      intent.save(saved); el("wtRetry").hidden = false;')
a=s.index('  async function retry()');b=s.index('  el("wtLoad")',a)
s=s[:a]+'''  async function retry() {
    if(busy)return;
    let record;const identity=owner();
    busy=true;el("wtRetry").disabled=true;el("wtApprove").disabled=true;
    try {
      record=intent.read();
      if(record.damaged)throw Error('Запрос повреждён. Архивируйте исходник и перечитайте волну.');
      if(!record.value)return;
      const result=await request('/approve-time','POST',record.value);
      if(identity!==owner())return;
      if(!intent.confirms(record.value,result))throw Error('Ответ не подтверждает исходное утверждение. Повторите сохранённый запрос.');
      intent.settle(record);reset();await load();
      message('Окно волны '+result.wave_id+' утверждено. Пересчитайте нагрузку; наличие дефицита проверяется отдельно.');
    } catch(error) {
      if(identity!==owner())return;
      if(record?.value&&intent.rejected(error))intent.settle(record);
      message(error.message+(pending()?' Повторите исходное утверждение.':' Перечитайте волну перед исправлением.'));
      el("wtRetry").hidden=!pending();
    } finally {
      busy=false;
      if(identity===owner()){el("wtRetry").disabled=false;el("wtApprove").disabled=!!pending()||!context||!auth().hasPermission('pick_wave_launch');}
    }
  }
'''+s[b:];p.write_text(s,encoding='utf-8')
