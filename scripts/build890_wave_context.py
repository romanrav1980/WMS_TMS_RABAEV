from pathlib import Path
import json
files={}
p="wiki-raw/wms_admin_ui_reference/wave-replenishment.js";s=Path(p).read_text(encoding="utf-8")
needle="function renderWaveRows(waves) {"
s=s.replace(needle,needle+"""
  const active=waveReplenishmentState.selectedWave;
  const pinned=active&&!waves.some(wave=>Number(wave.pick_wave_id)===Number(active.pick_wave_id));
  if(pinned){waves=[active,...waves];waveRepEl("waveReplenishmentSelectionText").textContent="Волна #"+active.pick_wave_id+" · "+(active.wave_code||"")+" · закреплена вне текущей выборки";}
""",1)
needle="  const epoch=++waveReplenishmentState.selectionEpoch,identity=waveRepIdentity();"
s=s.replace(needle,"""  for(const holder of [window.wmsWaveExecutionIntent,window.wmsWavePickIntent]){
    const saved=holder?.read().value;
    if(saved&&saved.wave!==waveId){waveRepEl('waveReplenishmentStatusText').textContent='Сначала повторите сохранённое решение волны '+saved.wave;return;}
  }
  window.dispatchEvent(new CustomEvent('wms-wave-selection-loading',{detail:{wave_id:waveId}}));
"""+needle,1)
s+="\nwindow.addEventListener('wms-wave-requested',event=>{const wave=Number(event.detail?.wave_id);if(Number.isSafeInteger(wave)&&wave>0)void selectWave(wave);else window.dispatchEvent(new CustomEvent('wms-wave-selection-loading',{detail:{wave_id:null}}));});\n"
files[p]=s
for p in ["wiki-raw/wms_admin_ui_reference/wave-execution.js","wiki-raw/wms_admin_ui_reference/wave-pick-release.js"]:
 s=Path(p).read_text(encoding="utf-8")
 s=s.replace("input.addEventListener('change',()=>choose(Number(input.value)));","input.addEventListener('change',()=>window.dispatchEvent(new CustomEvent('wms-wave-requested',{detail:{wave_id:Number(input.value)}})));")
 s=s.replace("  window.addEventListener('wms-wave-selected',", """  window.addEventListener('wms-wave-selection-loading',event=>{
    if(busy||record?.value)return;
    request++;snapshot=null;loading=true;input.value=event.detail?.wave_id||'';
    panel.querySelector('[data-items]').replaceChildren();status.textContent='Читаю выбранную волну…';controls();
  });
  window.addEventListener('wms-wave-selected',""",1)
 files[p]=s
p="wiki-raw/wms_admin_ui_reference/replenishment-progress.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace("input.addEventListener('change',()=>choose(Number(input.value)));","input.addEventListener('change',()=>window.dispatchEvent(new CustomEvent('wms-wave-requested',{detail:{wave_id:Number(input.value)}})));")
s=s.replace("  window.addEventListener('wms-wave-selected',", """  window.addEventListener('wms-wave-selection-loading',event=>{epoch++;input.value=event.detail?.wave_id||'';rowsTarget.replaceChildren();status.textContent='Читаю выбранную волну…';});
  window.addEventListener('wms-wave-selected',""",1);files[p]=s
p="wiki-raw/wms_admin_ui_reference/wave-source-availability.js";s=Path(p).read_text(encoding="utf-8");s=s.replace("  window.addEventListener('wms-wave-selected',", """  window.addEventListener('wms-wave-selection-loading',()=>{requestVersion++;context=null;next=null;target.hidden=true;});
  window.addEventListener('wms-wave-selected',""",1);files[p]=s
p="wiki-raw/wms_admin_ui_reference/wave-replenishment.html";s=Path(p).read_text(encoding="utf-8").replace('20261013-888','20261013-890').replace('20261013-880','20261013-890');files[p]=s
print(json.dumps(files,ensure_ascii=True))
