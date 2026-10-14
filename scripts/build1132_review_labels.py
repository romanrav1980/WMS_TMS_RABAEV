from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js");s=p.read_text(encoding="utf-8")
s=s.replace("if(result.trip_id!==trip||result.read_only!==true||!Array.isArray(result.routes))","if(result.trip_id!==trip||result.read_only!==true||!Array.isArray(result.routes)||result.routes.length!==1)")
s=s.replace("  ...(route?.capacity_and_type?.status==='BLOCKED'?[route.capacity_and_type.code]:[])];","  ...(route?.capacity_and_type?.status==='BLOCKED'?[route.capacity_and_type.code]:[])];")
s=s.replace(" const warnings=capacity?.warnings||[];"," const warnings=capacity?.warnings||[];\n const labels={PLAN_ST_FOREIGN_OR_SHIPPED:'СТ уже назначена в другой рейс или отгружена',PLAN_ST_NOT_FOUND:'СТ отсутствует',PLAN_ACTIVE_UNBILLED_TRIP_REQUIRED:'Рейс закрыт или включён в счёт',PLAN_ACTIVE_VEHICLE_CAPACITY_REQUIRED:'Машина заблокирована или не заданы её вместимость и тип',PLAN_CURRENT_VEHICLE_NOT_FOUND:'Машина не найдена',PLAN_WEIGHT_CAPACITY_EXCEEDED:'Превышена допустимая масса машины',PLAN_PALLET_CAPACITY_EXCEEDED:'Превышено число мест в машине',PLAN_ADDRESS_VEHICLE_TYPE_OR_HYDRO_CONFLICT:'Тип машины или гидроборт не соответствует магазину',PLAN_ADDRESS_VEHICLE_LIMIT_EXCEEDED:'Машина превышает ограничение магазина'};")
s=s.replace("blockers.join('; '):'Вместимость проверена действующими правилами ТМС.'","blockers.map(x=>labels[x]||x).join('; '):(capacity?.validation_status==='CAPACITY_TYPE_CHECKED'?'Вместимость проверена действующими правилами ТМС.':'План требует уточнения ограничений.')")
s=s.replace("(capacity?' Плановых мест: '","(capacity?.declared_places!==undefined&&capacity?.declared_weight_kg!==undefined?' Плановых мест: '")
print(json.dumps({str(p):s},ensure_ascii=True))
