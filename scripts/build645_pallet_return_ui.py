from pathlib import Path
import json
out={}
p=Path("admin/wms_admin_frontend/src/features/delivery/contracts.ts");v=p.read_text(encoding="utf-8").replace('level:"BOX";code:string','level:"BOX"|"PALLET";code:string');out[str(p)]=v
p=Path("admin/wms_admin_frontend/src/features/delivery/ReturnMarkPanel.tsx");v=p.read_text(encoding="utf-8")
v=v.replace('["UNIT","BOX","UNIT_OR_AGGREGATION"]','["UNIT","BOX","PALLET","UNIT_OR_AGGREGATION"]')
v=v.replace('const boxes=value.aggregation_scans.filter(x=>x.system_code===p.system_code&&x.profile_code===p.profile_code).length;','const boxes=value.aggregation_scans.filter(x=>x.system_code===p.system_code&&x.profile_code===p.profile_code&&(p.scan_mode==="UNIT_OR_AGGREGATION"||x.level===p.scan_mode)).length;')
v=v.replace('p.scan_mode==="BOX"?boxes>0','["BOX","PALLET"].includes(p.scan_mode)?boxes>0')
v=v.replace('x.level==="BOX"&&profiles.some(p=>p.system_code===x.system_code&&p.profile_code===x.profile_code&&["BOX","UNIT_OR_AGGREGATION"].includes(p.scan_mode))','["BOX","PALLET"].includes(x.level)&&profiles.some(p=>p.system_code===x.system_code&&p.profile_code===x.profile_code&&(p.scan_mode===x.level||p.scan_mode==="UNIT_OR_AGGREGATION"))')
v=v.replace('mode==="BOX"?"BOX":mode==="UNIT"?"UNIT":kind','mode==="BOX"||mode==="PALLET"?mode:mode==="UNIT"?"UNIT":kind')
v=v.replace('||mode==="PALLET"','')
v=v.replace('effectiveKind==="BOX"','effectiveKind!=="UNIT"')
v=v.replace('{...scan,level:"BOX"}','{...scan,level:effectiveKind as "BOX"|"PALLET"}')
a=' if(profiles.some(p=>p.scan_mode==="PALLET"))return <p>Возврат по агрегации паллеты требует сохранения её исходной идентичности. Передача заблокирована; обратитесь к логисту.</p>;'
assert a in v;v=v.replace(a,'')
v=v.replace('<option value="BOX">Агрегация коробки</option>','<option value="BOX">Агрегация коробки</option><option value="PALLET">Агрегация исходной паллеты</option>')
v=v.replace('effectiveKind!=="UNIT"?"Код агрегации коробки":"QR единицы"','effectiveKind==="PALLET"?"Код агрегации исходной паллеты":effectiveKind==="BOX"?"Код агрегации коробки":"QR единицы"')
v=v.replace('<p>QR единиц:', '<p>Для агрегации PALLET сохраните исходный идентификатор и полный неизменённый состав паллеты.</p>\n  <p>QR единиц:')
out[str(p)]=v
p=Path("wiki-raw/wms_admin_ui_reference/return-mark-draft.js");v=p.read_text(encoding="utf-8")
v=v.replace('["BOX","Агрегация коробки"]','["BOX","Агрегация коробки"],["PALLET","Агрегация исходной паллеты"]')
v=v.replace('["UNIT","BOX","UNIT_OR_AGGREGATION"]','["UNIT","BOX","PALLET","UNIT_OR_AGGREGATION"]')
v=v.replace('if(mode==="BOX")kind.value="BOX";','if(mode==="BOX"||mode==="PALLET")kind.value=mode;')
v=v.replace('kind.value==="BOX"?"Код агрегации коробки":"QR единицы"','kind.value==="PALLET"?"Код исходной паллеты (сохраните идентификатор) ":kind.value==="BOX"?"Код агрегации коробки":"QR единицы"')
v=v.replace('const box=kind.value==="BOX"','const box=kind.value!=="UNIT"')
v=v.replace('{level:"BOX"}','{level:kind.value}')
v=v.replace('(box?["BOX","UNIT_OR_AGGREGATION"]:["UNIT","UNIT_OR_AGGREGATION"]).includes(p.scan_mode)','(box?(p.scan_mode===x.level||p.scan_mode==="UNIT_OR_AGGREGATION"):["UNIT","UNIT_OR_AGGREGATION"].includes(p.scan_mode))')
v=v.replace('(!box||x.level==="BOX")','(!box||["BOX","PALLET"].includes(x.level))')
v=v.replace('throw Error("Возврат по агрегации паллеты требует сохранения исходной идентичности. Обратитесь к логисту.")','throw Error("Неподдерживаемый профиль маркировки возврата.")')
v=v.replace('draft.aggregation_scans.filter(matches).length','draft.aggregation_scans.filter(x=>matches(x)&&(p.scan_mode==="UNIT_OR_AGGREGATION"||x.level===p.scan_mode)).length')
v=v.replace('p.scan_mode==="BOX"?boxes>0','["BOX","PALLET"].includes(p.scan_mode)?boxes>0')
out[str(p)]=v
print(json.dumps(out,ensure_ascii=True))
