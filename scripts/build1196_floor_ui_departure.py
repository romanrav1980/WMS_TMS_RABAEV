from pathlib import Path
import json
f={}
p=Path("api/wms_api_server/app/modules/transport/infrastructure/loading_status.py");s=p.read_text(encoding="utf-8")
s=s.replace("from .loading_thermal_read import loading_thermal_read","from .loading_thermal_read import loading_thermal_read\nfrom .loading_floor_read import loading_floor_read",1)
point='    return {"trip":dict(zip'
assert point in s;s=s.replace(point,'    floor=loading_floor_read(cur,[row["load_operation_id"]for row in loads],trip)\n'+point,1)
s=s.replace('"physical_places":loads,"temperature":thermal,','"physical_places":loads,"temperature":thermal,"floor_capacity":floor,',1);f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/transport-loading.js");s=p.read_text(encoding="utf-8")
old='[item.st_number,item.root_uid||"",item.load_status||"Ожидает",item.vehicle_number||"",item.dock||"",data.temperature?'
new='[item.st_number,item.root_uid||"",item.load_status||"Ожидает",item.vehicle_number||"",item.dock||"",data.floor_capacity?.load_confirmations?.[item.load_operation_id]?.current_type_name||"Тип верхнего места не подтверждён",data.temperature?'
assert old in s;s=s.replace(old,new,1)
point='  window.dispatchEvent(new CustomEvent("wms-physical-load-status"'
insert="""  const floor=data.floor_capacity?.departure_confirmation;
  if(floor?.status==="COMPATIBLE")el("departTempProfile").textContent+=" Норматив тары на выезде подтверждён: "+floor.matching_variants.join(", ")+"; верхних мест "+floor.loaded_top_places+".";
"""
assert point in s;s=s.replace(point,insert+point,1);f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/transport-loading.html");s=p.read_text(encoding="utf-8").replace("<th>Температура при погрузке</th>","<th>Тип верхнего места</th><th>Температура при погрузке</th>",1).replace("20261014-1176","20261014-1196");f[str(p)]=s
s=Path("scripts/case1172_departure_temperature.py").read_text(encoding="utf-8").replace("context1168.json","context1194.json").replace('d["load_operation_id"]','d["load_operation"]').replace("THERMAL1172","FLOOR1196").replace("DEV1172","DEV1196").replace('"vehicle_profile_version":1','"vehicle_profile_version":2')
s=s.replace('q.execute("select OBSERVED_C','q.execute("select OBSERVED_C',1)
point='  q.execute("select STATUS from RRL_TT_HU_LOAD_FACT'
s=s.replace(point,'  assert result["floor_at_departure"]["status"]=="COMPATIBLE" and result["floor_at_departure"]["loaded_top_places"]==1\n'+point,1)
point='assert result["stock_consumed_again"]is False'
s=s.replace(point,point+'\nassert result["floor_at_departure"]["status"]=="COMPATIBLE" and result["floor_at_departure"]["counts"]==[{"pallet_type_id":1,"places":1}]',1)
old='context_path.write_text(json.dumps(d,indent=2),encoding="utf-8")'
# Original protected source ends with saved state/result; preserve it and own durable case.
s=s.replace('PASS1172','PASS1196')
f["scripts/case1196_departure_floor.py"]=s
print(json.dumps(f))
