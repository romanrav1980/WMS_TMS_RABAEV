from pathlib import Path
import json
f={}
p="api/wms_api_server/app/modules/inventory/infrastructure/wave_execution_reader.py";s=Path(p).read_text(encoding="utf-8")
old="                where h.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID and r.REMAIN>0) STOCK_ROWS\n            from RRL_CASE_PICK_TASK ct where ct.PICK_WAVE_ID=:p_wave"
new="""                where h.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID and r.REMAIN>0) STOCK_ROWS,
            ct.CONTENT_VERSION,ct.CURRENT_CELL,ct.SSCC,st.PALLET_UID
            from RRL_CASE_PICK_TASK ct left join RRL_SBORKA_PALLETS st on st.ID=ct.LEGACY_SBORKA_PALLET_ID
            where ct.PICK_WAVE_ID=:p_wave"""
assert old in s;s=s.replace(old,new,1)
old='            item["quantity_semantics"] = "HISTORICAL_PICKED"'
assert old in s
s=s.replace(old,old+'''
            item["case_content_version"] = int(row[4])
            item["current_cell"] = row[5]
            item["carrier_identifier"] = row[6]
            item["control_identifier"] = row[7]''',1)
f[p]=s
p="wiki-raw/wms_admin_ui_reference/wave-execution-view.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace("RESERVATION:'Резерв'","RESERVATION:'Резерв',HARD:'Жёсткий резерв'",1)
s=s.replace("      row.append(name);\n      const reason","""      if(item.kind==='CASE'){
        const info=document.createElement('small');info.className='wave-execution-place';
        info.textContent=[item.carrier_identifier,item.current_cell?'Ячейка '+item.current_cell:null,
          item.case_content_version!==undefined?'Состав v'+item.case_content_version:null].filter(Boolean).join(' · ');
        name.append(info);
      }
      row.append(name);
      const reason""",1)
s=s.replace("item.quantity??'—',item.actor","(item.quantity??'—')+(item.quantity_semantics==='HISTORICAL_PICKED'?' · факт отбора':''),item.actor",1)
s=s.replace("      if(reason && !data.completed)row.className=", """      if(item.kind==='CASE'&&/^[1-9]\\d*$/.test(String(item.id))){
        const actions=row.lastChild,links=document.createElement('div');links.className='wave-execution-actions';
        const composition=document.createElement('a');composition.className='wave-execution-action';
        composition.href='warehouse-hus.html?identifier='+encodeURIComponent('CASE:'+item.id)+'#huComposition';
        composition.textContent='Текущий состав';composition.title='Проверить фактическое место, партии и резерв';links.append(composition);
        if(!data.completed&&typeof item.control_identifier==='string'&&item.control_identifier&&
          window.wmsAdminAuth?.hasPermission('outgoing_pallet_check')){
          const control=document.createElement('a');control.className='wave-execution-action primary';
          control.href='warehouse-tasks.html?qc_shipment='+encodeURIComponent(item.control_identifier)+'#outgoingQuality';
          control.textContent='Открыть контроль';control.title='Предъявить текущий состав в существующем процессе контроля';links.append(control);
        }
        actions.append(links);
      }
      if(reason && !data.completed)row.className=""",1)
f[p]=s
p="wiki-raw/wms_admin_ui_reference/outgoing-quality.js";s=Path(p).read_text(encoding="utf-8").replace('panel.className="panel";','panel.className="panel";panel.id="outgoingQuality";',1)
s=s.replace('Выгруженная СТ: предъявите актуальный состав к повторному контролю.','Выбрана СТ: предъявите актуальный состав к контролю.')
f[p]=s
p="wiki-raw/wms_admin_ui_reference/wave-execution.css";f[p]=Path(p).read_text(encoding="utf-8")+"""
.wave-execution-place{display:block;margin-top:7px;max-width:310px;color:#61748d;font-size:12px;line-height:1.6;overflow-wrap:anywhere}
.wave-execution-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.wave-execution-action{display:inline-flex;align-items:center;padding:7px 10px;border:1px solid #cbdbf1;border-radius:7px;background:#fff;color:#2561a8;font:600 12px "Segoe UI",sans-serif;text-decoration:none;white-space:nowrap}
.wave-execution-action.primary{background:#eaf2ff;border-color:#acc9f0}.wave-execution-action:hover{background:#dceaff}
"""
for p in("wiki-raw/wms_admin_ui_reference/wave-replenishment.html","wiki-raw/wms_admin_ui_reference/warehouse-tasks.html"):
 import re
 s=Path(p).read_text(encoding="utf-8")
 for asset in("wave-execution-view.js","wave-execution.css","outgoing-quality.js"):
  s=re.sub(re.escape(asset)+r'(?:\?v=[^"\']*)?',asset+"?v=20261013-1092",s)
 f[p]=s
p="wiki/components/nicora_ni033_wave_workspace_20261013.md"
f[p]=Path(p).read_text(encoding="utf-8")+"\n1092: bounded current wave read adds CASE currentcell/carrier/version and actual existing ST control identifier in same READONLY snapshot after scope. UI links to existing composition/QC, per-item picking history labelled separately from currentstock. No QC/stock/wave status writes; actual runtime/current source553 andbrowser next. Owner inventory, same existing Root finish command, no second quality module.\n"
f["wiki/index.md"]="- [Wave next actions1092](components/nicora_ni033_wave_workspace_20261013.md): current CASE carrier/cell/version and existing QC/composition links; currentwave553 pendingcontrol, no status bypass.\n"+Path("wiki/index.md").read_text(encoding="utf-8")
f["wiki/log.md"]=Path("wiki/log.md").read_text(encoding="utf-8")+"\n-1092: NI03.3 remaining workflow functional next actions reuse existing QC andcomposition. Actualwave553blockedbycurrentWAIT_CONTROL/HARD, correctnotclosed. Native currentread1090/QC1091, no stock changed; bounded scoped reader/UI extension prepared.\n"
print(json.dumps(f,ensure_ascii=True))
