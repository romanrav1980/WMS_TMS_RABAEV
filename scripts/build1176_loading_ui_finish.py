from pathlib import Path
import json
f={}
p=Path("wiki-raw/wms_admin_ui_reference/transport-loading.js");s=p.read_text(encoding="utf-8")
point='el("loadRestart").hidden=!pending?.confirmed_rejection;'
s=s.replace(point,point+'el("tripDepart").disabled=busy||!!pending||trip?.trip?.condition!=="Спланирован"||!trip?.all_members_physically_loaded;el("loadConfirm").disabled=busy||!!pending||trip?.trip?.condition!=="Спланирован";',1)
s=s.replace('[item.st_number,item.root_uid||"",item.load_status||"Ожидает",item.vehicle_number||"",item.dock||""]','[item.st_number,item.root_uid||"",item.load_status||"Ожидает",item.vehicle_number||"",item.dock||"",data.temperature?.load_confirmations?.[item.load_operation_id]?.confirmation?.observed_c?data.temperature.load_confirmations[item.load_operation_id].confirmation.observed_c+" °C · вручную":"Не подтверждена"]',1)
s=s.replace('  }));\n }','  }));controls();\n }',1)
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/transport-loading.html");s=p.read_text(encoding="utf-8")
s=s.replace('<th>Ворота</th></tr>','<th>Ворота</th><th>Температура при погрузке</th></tr>',1)
s=s.replace('<fieldset><legend>Температура непосредственно','<fieldset class="loading-temperature"><legend>Температура непосредственно',1)
s=s.replace('<h2>Выезд</h2><p id="departTempProfile">','<h2>Выезд</h2><fieldset class="loading-temperature"><legend>Новое измерение перед выездом</legend><p id="departTempProfile">',1)
s=s.replace('<button id="tripDepart">','</fieldset><button id="tripDepart">',1)
s=s.replace('transport-loading.js?v=20261014-1171','transport-loading.js?v=20261014-1176')
s=s.replace('</head>','<link rel="stylesheet" href="transport-loading-temperature.css?v=20261014-1176"></head>',1)
f[str(p)]=s
# Fix fixture source as reproducible source; never rerun existing1168 factory.
p=Path("scripts/case1168_loading_temperature.py");s=p.read_text(encoding="utf-8")
s=s.replace("RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,TEMP_MIN,TEMP_MAX)values(:ware,:a,2,6)","RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,TEMP_MIN,TEMP_MAX)values(:ware,:a,:cell,2,6)").replace('a=article)\n from app.modules.transport.infrastructure.vehicle_profile','a=article,cell=dst)\n from app.modules.transport.infrastructure.vehicle_profile',1)
f[str(p)]=s
print(json.dumps(f))
