from pathlib import Path
import json
f={}
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js");s=p.read_text(encoding="utf-8")
point=" const thermalNote=thermal?("
insert=""" const thermalPlanning=thermal?.planning;
 const thermalPlanningNote=thermalPlanning?(
  thermalPlanning.status==='DECLARED_CAPABILITY_COMPATIBLE'?' По текущему профилю машины достижим диапазон '+thermalPlanning.feasible_min_c+' … '+thermalPlanning.feasible_max_c+' °C. Фактическая температура ещё не подтверждена.':
  thermalPlanning.status==='VEHICLE_RANGE_INCOMPATIBLE'?' Температурные возможности машины несовместимы с товаром.':
  thermalPlanning.status==='SKU_RANGES_CONFLICT'?' Для этих товаров нет общего температурного режима.':
  ' Совместимость температурного профиля не подтверждена: '+thermalPlanning.status+'.'):'';
"""
assert point in s;s=s.replace(point,insert+point).replace("+thermalNote;","+thermalNote+thermalPlanningNote;")
# The final formatter may contain further suffixes: inspect replacement precisely.
s=s.replace("+thermalNote+"," +thermalNote+thermalPlanningNote+")
f[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/finance/VehiclePhysicalProfile.tsx");s=p.read_text(encoding="utf-8")
s=s.replace("if(running.current||blocked)return;running.current=true;setBusy(true);const key=scope;","""if(running.current||blocked)return;
  const raw=localStorage.getItem(scope);
  if(current.current!==scope||raw!==JSON.stringify(intent)){setBlocked(true);setMessage("Сохранённая операция изменилась. Отправка остановлена; перечитайте карточку.");return;}
  running.current=true;setBusy(true);const key=scope;""")
s=s.replace("   localStorage.removeItem(key);","""   if(current.current!==key||localStorage.getItem(key)!==raw)return;
   localStorage.removeItem(key);""")
s=s.replace("  }catch(e){if(current.current===key){","  }catch(e){if(current.current===key&&localStorage.getItem(key)===raw){")
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");f[str(p)]=p.read_text(encoding="utf-8").replace("customer-orders.js?v=20261013-1133","customer-orders.js?v=20261014-1153")
print(json.dumps(f))
