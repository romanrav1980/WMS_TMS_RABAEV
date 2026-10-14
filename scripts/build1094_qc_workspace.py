from pathlib import Path
import json
f={};p="wiki-raw/wms_admin_ui_reference/outgoing-quality.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace('panel.className="panel";','panel.className="panel qc-workspace";',1)
start=s.index(" panel.innerHTML=");end=s.index("\n (document.querySelector",start)
s=s[:start]+""" panel.innerHTML='<header class="qc-header"><div><p>ПРОВЕРКА ГРУЗА</p><h2>Контроль перед отгрузкой</h2></div><span data-admission class="qc-admission">Состав не прочитан</span></header>'+
 '<div class="qc-toolbar"><label>Идентификатор СТ <input data-id autocomplete="off"></label><button data-load>Предъявить к контролю</button><button data-print-label>Этикетка допуска / красный тег</button></div>'+
 '<p data-summary class="qc-summary">Предъявите грузовое место. Допуск относится к подтверждённой версии состава.</p>'+
 '<div class="qc-columns"><section class="qc-stage"><h3>1 · Сверка состава</h3><div data-items class="qc-entry"><label>Штрихкод штуки или целой коробки <input data-item-code autocomplete="off"></label><button data-add-item>Добавить скан</button></div>'+
 '<div data-marks class="qc-marks"><label>Система / профиль <select data-profile></select></label><label>QR единицы товара <input data-code autocomplete="off"></label><button data-add-mark>Добавить QR</button></div>'+
 '<div class="qc-actions"><button data-last>Удалить последний скан</button><button data-clear>Очистить новые сканы</button></div><p data-count class="qc-count"></p><div class="qc-entry"><label>Ошибок сканирования <input data-errors type="number" min="0" step="1" value="0"></label><button data-scan class="qc-primary">Подтвердить сканирование</button></div></section>'+
 '<section class="qc-stage"><h3>2 · Контроль веса</h3><p>Используйте фактическое показание весов и вес тары в килограммах.</p><div class="qc-entry"><label>Вес брутто, кг <input data-gross inputmode="decimal"></label><label>Вес тары, кг <input data-tare inputmode="decimal" value="0"></label></div>'+
 '<label>Режим веса <select data-kind><option value="WEIGHT2">Контроль веса перед погрузкой</option><option value="WEIGHT">Контроль веса</option></select></label><button data-weight class="qc-primary">Подтвердить вес</button></section></div><p role="status" aria-live="polite"></p>';
"""+s[end:]
s=s.replace('QUALITY_FOREIGN_ITEM_BARCODE:"', 'QUALITY_SI_WEIGHT_POLICY_REQUIRED:"В карточке товара отсутствуют весовые нормативы для контроля.",\n   QUALITY_FOREIGN_ITEM_BARCODE:"',1)
s=s.replace('  const r=await fetch(base()+url,','  const scope=key(),r=await fetch(base()+url,',1)
needle='),data=await r.json();\n  if(!r.ok)'
assert needle in s
s=s.replace(needle,'),data=await r.json();\n  if(scope!==key()){const error=Error("Пользователь или API изменился.");error.obsolete=true;throw error;}\n  if(!r.ok)',1)
needle='  snapshot=data;finalReadings();'
assert needle in s
s=s.replace(needle,'''  el("admission").textContent=data.ready?"Допуск подтверждён":"Ожидает контроля";el("admission").className="qc-admission"+(data.ready?" ready":" pending");
  el("summary").textContent=["СТ "+data.shipment_identifier,data.case_content_version!==undefined?"Состав v"+data.case_content_version:null,
   "Режим "+(data.control_mode||"по настройке"),data.independent_controller_required?"Независимый контролёр":null,
   data.unique_mark_control_required?"Уникальные коды обязательны":"Обычные штрихкоды"].filter(Boolean).join(" · ");
'''+needle,1)
s=s.replace(':" "+(data.weight_policy_reason||""));',':" "+explain(data.weight_policy_reason));',1)
s=s.replace('  const sent=pending;','  const sent=pending,savedKey=key(),savedRaw=localStorage.getItem(savedKey);',1)
needle='   localStorage.removeItem(key());pending=null;'
assert needle in s
s=s.replace(needle,'''   if(result.operation_id!==sent.body.operation_id||(sent.kind==="plan"&&
     (result.control_status?.shipment_identifier!==sent.identifier||result.control_status?.composition_signature!==sent.body.expected_composition_signature)))
    throw Error("Ответ не соответствует исходной операции. Повторите сохранённую команду.");
   if(localStorage.getItem(savedKey)!==savedRaw)throw Error("Исходная команда изменилась в другой вкладке.");
   localStorage.removeItem(savedKey);pending=null;''',1)
s=s.replace('  }catch(e){\n   if(e.detail?.outcome_confirmed===true)', '  }catch(e){\n   if(e.obsolete)return;\n   if(e.detail?.outcome_confirmed===true&&e.detail.operation_id===sent.body.operation_id&&localStorage.getItem(savedKey)===savedRaw)',1)
s=s.replace('  }catch(e){message.textContent=e.message;}\n }\n function currentDraft','  }catch(e){if(!e.obsolete)message.textContent=e.message;}\n }\n function currentDraft',1)
needle='if(requested && requested.length<=150){el("id").value=requested;message.textContent="Выбрана СТ: предъявите актуальный состав к контролю.";}'
assert needle in s
s=s.replace(needle,'''if(requested && requested.length<=150){
      el("id").value=requested;const current=++generation;
      message.textContent="Читается текущий состав выбранной СТ.";
      call(path(requested)).then(data=>{if(current===generation&&el("id").value.trim()===requested)show(data);})
        .catch(error=>{if(current===generation&&!error.obsolete)message.textContent=error.message;});
     }''',1)
f[p]=s
p="wiki-raw/wms_admin_ui_reference/outgoing-quality.css"
f[p]=""".qc-workspace{margin-bottom:22px;padding:0!important;overflow:hidden;border:1px solid #dfe7f2;border-radius:14px;background:#fff}
.qc-header{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:20px 24px;border-bottom:1px solid #edf1f7}.qc-header h2{margin:4px 0!important;font-size:21px}.qc-header p{margin:0;color:#66809e;font-size:11px;font-weight:700;letter-spacing:1px}
.qc-admission{padding:8px 12px;border-radius:20px;background:#eef3fa;color:#607693;font-size:12px;font-weight:700;white-space:nowrap}.qc-admission.pending{background:#fff3db;color:#976518}.qc-admission.ready{background:#e8f6ed;color:#288153}
.qc-toolbar{display:flex;align-items:end;gap:12px;padding:20px 24px;flex-wrap:wrap}.qc-toolbar>label{flex:1;min-width:260px}.qc-workspace label{display:flex;flex-direction:column;gap:6px;font-size:12px;color:#5c718d}.qc-workspace input,.qc-workspace select{padding:10px 12px;border:1px solid #d8e2f0;border-radius:8px;background:#fff;font:14px "Segoe UI",sans-serif;color:#203b5b;min-width:0}
.qc-workspace button{border:1px solid #c6d9f4;border-radius:8px;padding:10px 13px;background:#eef5ff;color:#2866b2;font:600 12px "Segoe UI",sans-serif;cursor:pointer}.qc-workspace button:disabled{opacity:.45;cursor:default}.qc-workspace button.qc-primary{background:#2a75d9;color:#fff;border-color:#2a75d9}
.qc-summary{margin:0 24px!important;padding:13px 15px;background:#f0f5fd;border-radius:9px;color:#426080;line-height:1.7;font-size:13px}
.qc-columns{display:grid;grid-template-columns:1.15fr 1fr;gap:18px;padding:20px 24px}.qc-stage{border:1px solid #e2eaf5;border-radius:10px;padding:18px;background:#fcfdff}.qc-stage h3{margin:0 0 15px;font-size:16px;color:#274e79}.qc-stage>p{font-size:12px;color:#677d99;line-height:1.7}.qc-entry,.qc-marks,.qc-actions{display:flex;align-items:end;gap:10px;flex-wrap:wrap;margin:12px 0}.qc-entry>label,.qc-marks>label{flex:1;min-width:140px}.qc-count{font-size:12px;color:#617793}.qc-stage>label{margin:14px 0}.qc-workspace>[role=status]{margin:0 24px 20px;padding:15px;border-radius:9px;background:#f5f8fc;color:#4d6480;font-size:13px;line-height:1.7;overflow-wrap:anywhere}.qc-workspace>div:not(.qc-toolbar):not(.qc-columns){margin:0 24px 20px}
@media(max-width:900px){.qc-columns{grid-template-columns:1fr}.qc-header{align-items:start;flex-wrap:wrap}.qc-toolbar>button{flex:1}.qc-toolbar>label{min-width:100%}}
"""
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.html";t=Path(p).read_text(encoding="utf-8")
t=t.replace('</head>','<link rel="stylesheet" href="outgoing-quality.css?v=20261013-1094"></head>',1).replace("outgoing-quality.js?v=20261013-1092","outgoing-quality.js?v=20261013-1094")
f[p]=t
p="wiki/components/retailcase_ni051_control_label_20261012.md"
f[p]=Path(p).read_text(encoding="utf-8")+"\n1094: существующий QC ARM оформлен как отдельные сверка состава/вес, текущий допуск/версия/режим/независимость. qc_shipment link читает только GET status; не запускает PLAN автоматически. Старый pending/draft имеет приоритет. Response actor/API scope, exact operation/control identifier/signature andcross-tab raw compare защищают сохранённую команду перед очисткой. Авторская targetedproof/browser next, nativeQC rules unchanged.\n"
f["wiki/index.md"]="- [QC workspace1094](components/retailcase_ni051_control_label_20261012.md): linked readonly status, separate scan/weight stages and exact response/pending scope guards.\n"+Path("wiki/index.md").read_text(encoding="utf-8")
f["wiki/log.md"]=Path("wiki/log.md").read_text(encoding="utf-8")+"\n-1094: continued NI03.3→existingNI05.1 QC workflow; functional readable ARM/read-only link/currentversion, operation correlation+cross-tab+actor guard added without QC rule changes. Runtimepending.\n"
print(json.dumps(f,ensure_ascii=True))
