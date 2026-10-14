import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py");s=p.read_text(encoding="utf-8")
anchor='            q.execute("""select r.OPERATION_ID,r.RECEIVE_CELL,pp.TASK_ID,t.STATUS,t.HU_CONTENT_VERSION,'
assert anchor in s
new='''            q.execute("""select distinct card.ARTICUL,card.SYSTEM_CODE,card.PROFILE_CODE,card.PROFILE_VERSION,card.SCAN_MODE
                from json_table(:source_json,'$.lots[*]'columns(A varchar2(160)path '$.article'))selected
                join RRL_SKU_RECEIPT_PROFILE card on card.ARTICUL=selected.A
                order by card.ARTICUL,card.SYSTEM_CODE,card.PROFILE_CODE fetch first 4001 rows only""",source_json=__import__("json").dumps(source))
            current_profiles=q.fetchall()
            if len(current_profiles)>4000:
                raise StoreReturnReceiveError("INTERWARE_GROUP_PROFILE_BOUND","Profile matrix exceeds 4000",422)
            for lot in lots:
                lot["scan_profiles"]=[dict(system_code=card[1],profile_code=card[2],profile_version=card[3],scan_mode=card[4])for card in current_profiles if card[0]==lot["article"]]
'''+anchor
s=s.replace(anchor,new);out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse-groups.html");s=p.read_text(encoding="utf-8")
s=s.replace('отсканируйте все обязательные профили маркировки каждой единицы.','подтвердите все обязательные профили маркировки: QR единиц или разрешённые карточкой агрегаты коробки/паллеты.')
s=s.replace('<label>QR единицы<input id="ggCode"','<label>Способ сканирования<select id="ggScanMode"><option value="UNIT">QR единицы</option><option value="BOX">Агрегация коробки</option><option value="PALLET">Агрегация паллеты</option></select></label><label>Уникальный код или код агрегации<input id="ggCode"')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse-groups.js");s=p.read_text(encoding="utf-8")
s=s.replace('for(const p of lot.profiles)profiles.push(new Option(lot.article+" · "+p.system_code+"/"+p.profile_code,JSON.stringify({system_code:p.system_code,profile_code:p.profile_code})));','for(const p of lot.scan_profiles||lot.profiles)profiles.push(new Option(lot.article+" · "+p.system_code+"/"+p.profile_code+" · "+(p.scan_mode||"UNIT"),JSON.stringify({system_code:p.system_code,profile_code:p.profile_code,scan_mode:p.scan_mode||"UNIT"})));')
s=s.replace('const profile=JSON.parse(el("ggProfile").value);','const profile=JSON.parse(el("ggProfile").value),mode=el("ggScanMode").value;\n if(profile.scan_mode!==mode&&!(mode==="UNIT"&&profile.scan_mode==="UNIT")&&profile.scan_mode!=="UNIT_OR_AGGREGATION")throw Error("Способ сканирования не разрешён текущей карточкой товара");')
s=s.replace('const next=[...scans,{...profile,code}];','const evidence={system_code:profile.system_code,profile_code:profile.profile_code,code,...(mode==="UNIT"?{}:{level:mode})};\n const values=scans.filter(s=>!!s.level===!!evidence.level);if(values.length>=(evidence.level?1000:20000))throw Error("Превышена граница состава сканов");\n const next=[...scans,evidence];')
s=s.replace('items,scans:scans.map(s=>({...s}))','items,scans:scans.filter(s=>!s.level).map(s=>({...s})),...(scans.some(s=>s.level)?{aggregation_scans:scans.filter(s=>s.level).map(s=>({...s}))}:{})')
s=s.replace('"Сканов: "+scans.length+" · требуется: "', '"Сканов единиц: "+scans.filter(s=>!s.level).length+" · агрегатов: "+scans.filter(s=>s.level).length+" · матрица единиц/профилей: "')
out[str(p)]=s
print(json.dumps(out))
