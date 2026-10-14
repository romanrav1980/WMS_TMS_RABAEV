from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('<label>QR физической единицы <input id="iwUnitCode"','<label>Способ сканирования <select id="iwUnitLevel"><option value="UNIT">QR единицы</option><option value="BOX">Код коробки</option><option value="PALLET">Код паллеты</option></select></label><label>Отсканированный код <input id="iwUnitCode"',1)
s=s.replace('JSON.stringify([p.system_code,p.profile_code])','JSON.stringify([p.system_code,p.profile_code,p.scan_mode])',1)
a=s.index('   el("iwUnitInfo").textContent="Физических единиц: "');b=s.index('\n',a)
s=s[:a]+'   el("iwUnitInfo").textContent="Физических единиц: "+source.physical_unit_count+". Сканируйте единицы или зарегистрированную агрегацию согласно режиму карточки. Состав агрегации проверяет сервер; количество товара подтверждается отдельно.";'+s[b:]
s=s.replace('const [system_code,profile_code]=JSON.parse(el("iwUnitProfile").value),code=el("iwUnitCode").value;','const [system_code,profile_code,mode]=JSON.parse(el("iwUnitProfile").value),code=el("iwUnitCode").value,level=el("iwUnitLevel").value;\n  if(mode!=="UNIT_OR_AGGREGATION"&&mode!==level)throw Error("Этот способ сканирования не разрешён текущим профилем.");',1)
s=s.replace('saveScans([...unitScans,{system_code,profile_code,code}],plan);','if(level!=="UNIT"&&unitScans.filter(s=>s.level).length>=1000)throw Error("Превышен предел агрегационных сканов.");\n  saveScans([...unitScans,{system_code,profile_code,code,...(level==="UNIT"?{}:{level})}],plan);',1)
s=s.replace('body.scans=unitScans.map(s=>({...s}));','const singles=unitScans.filter(s=>!s.level),groups=unitScans.filter(s=>s.level);if(singles.length)body.scans=singles.map(s=>({...s}));if(groups.length)body.aggregation_scans=groups.map(s=>({...s}));',1)
s=s.replace('el("iwUnitCount").textContent="Сканов: "+unitScans.length','el("iwUnitCount").textContent="Сканов: "+unitScans.filter(s=>!s.level).length+" QR + "+unitScans.filter(s=>s.level).length+" агрегаций"',1)
print(json.dumps({p.as_posix():s}))
