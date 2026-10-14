from pathlib import Path
import json
p="wiki-raw/wms_admin_ui_reference/wave-replenishment.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace("  selectedWave: null,","  selectedWave: null,\n  listEpoch: 0,\n  selectionEpoch: 0,\n  initialWaveId: null,",1)
s=s.replace('const waveRepEl = (id) => document.getElementById(id);','const waveRepEl = (id) => document.getElementById(id);\nconst waveRepIdentity=()=>JSON.stringify([waveRepApiBase(),window.wmsAdminAuth?.state?.user?.username]);')
a=s.index("async function loadWaveReplenishmentWaves() {");b=s.index("\nfunction renderWaveRows",a)
s=s[:a]+"""async function loadWaveReplenishmentWaves() {
  waveRepEl("waveReplenishmentStatusText").textContent="Загрузка...";
  const epoch=++waveReplenishmentState.listEpoch,identity=waveRepIdentity(),params=waveRepWaveParams().toString();
  const rows=await waveRepFetch('/api/picking/waves?'+params);
  if(epoch!==waveReplenishmentState.listEpoch||identity!==waveRepIdentity()||params!==waveRepWaveParams().toString())return;
  waveReplenishmentState.waves=rows;
  const query=waveRepEl("waveReplenishmentSearch").value.trim().toLowerCase();
  const waves=query?rows.filter(wave=>[wave.pick_wave_id,wave.wave_code,wave.wave_name,wave.status]
    .some(value=>String(value||'').toLowerCase().includes(query))):rows;
  renderWaveRows(waves);waveRepEl("waveReplenishmentStatusText").textContent='Волн: '+waves.length;
  if(waveReplenishmentState.initialWaveId){
    const id=waveReplenishmentState.initialWaveId;waveReplenishmentState.initialWaveId=null;
    await selectWave(id);
  }
}
"""+s[b:]
a=s.index("async function selectWave(waveId) {");b=s.index("\nfunction renderReplenishmentTasks",a)
s=s[:a]+"""async function selectWave(waveId) {
  if(!Number.isSafeInteger(waveId)||waveId<1)return;
  const epoch=++waveReplenishmentState.selectionEpoch,identity=waveRepIdentity();
  waveReplenishmentState.selectedWave=null;waveReplenishmentState.tasks=[];waveReplenishmentState.stagingTasks=[];
  renderReplenishmentTasks();renderStagingTasks();
  waveRepEl("waveReplenishmentSelectionText").textContent='Читаю волну #'+waveId;
  try{
    const wave=waveReplenishmentState.waves.find(item=>Number(item.pick_wave_id)===waveId)||
      await waveRepFetch('/api/picking/waves/'+waveId+'/header');
    if(epoch!==waveReplenishmentState.selectionEpoch||identity!==waveRepIdentity())return;
    if(Number(wave?.pick_wave_id)!==waveId)throw new Error('Ответ не соответствует выбранной волне.');
    waveReplenishmentState.selectedWave=wave;
    waveRepEl("waveReplenishmentSelectionText").textContent='Волна #'+waveId+' · '+(wave.wave_code||'');
    window.dispatchEvent(new CustomEvent('wms-wave-selected',{detail:{wave_id:waveId}}));
    const results=await Promise.allSettled([loadWaveReplenishmentTasks(),loadWaveStagingTasks()]);
    if(epoch!==waveReplenishmentState.selectionEpoch||identity!==waveRepIdentity())return;
    const failed=results.find(result=>result.status==='rejected');if(failed)throw failed.reason;
    renderWaveRows(waveReplenishmentState.waves);
  }catch(error){if(epoch===waveReplenishmentState.selectionEpoch&&identity===waveRepIdentity())showWaveRepError(error);}
}

async function loadWaveReplenishmentTasks() {
  const wave=waveReplenishmentState.selectedWave;if(!wave)return;
  const epoch=waveReplenishmentState.selectionEpoch,identity=waveRepIdentity();
  waveRepEl("waveReplenishmentDetailStatus").textContent="Загрузка пополнений...";
  const rows=await waveRepFetch('/api/picking/waves/'+wave.pick_wave_id+'/replenishment-tasks?limit=500');
  if(epoch!==waveReplenishmentState.selectionEpoch||identity!==waveRepIdentity()||
    waveReplenishmentState.selectedWave?.pick_wave_id!==wave.pick_wave_id)return;
  waveReplenishmentState.tasks=rows;renderReplenishmentTasks();
}
"""+s[b:]
a=s.index("async function loadWaveStagingTasks() {");b=s.index("\nfunction renderStagingTasks",a)
s=s[:a]+"""async function loadWaveStagingTasks() {
  const wave=waveReplenishmentState.selectedWave;if(!wave)return;
  const epoch=waveReplenishmentState.selectionEpoch,identity=waveRepIdentity();
  const rows=await waveRepFetch('/api/picking/waves/'+wave.pick_wave_id+'/tasks?limit=500');
  if(epoch!==waveReplenishmentState.selectionEpoch||identity!==waveRepIdentity()||
    waveReplenishmentState.selectedWave?.pick_wave_id!==wave.pick_wave_id)return;
  waveReplenishmentState.stagingTasks=rows.filter(row=>row.task_type==='FULL_PALLET');renderStagingTasks();
}
"""+s[b:]
s=s.replace("function initWaveReplenishmentPage() {","function initWaveReplenishmentPage() {\n  waveReplenishmentState.initialWaveId=Number(new URLSearchParams(location.search).get('wave_id'))||null;",1)
files={p:s}
p="wiki-raw/wms_admin_ui_reference/wave-source-availability.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace('  target.querySelector("[data-source-next]").addEventListener',"""  window.addEventListener('wms-wave-selected',()=>{requestVersion++;context=null;next=null;target.hidden=true;});
  window.addEventListener('wms-admin-auth-ready',()=>{requestVersion++;context=null;next=null;target.hidden=true;});
  target.querySelector("[data-source-next]").addEventListener""",1)
files[p]=s
p="wiki-raw/wms_admin_ui_reference/wave-replenishment.html";s=Path(p).read_text(encoding="utf-8").replace('<script src="wave-replenishment.js">','<script src="wave-replenishment.js?v=20261013-888">').replace('<script src="wave-source-availability.js">','<script src="wave-source-availability.js?v=20261013-888">');files[p]=s
print(json.dumps(files,ensure_ascii=True))
