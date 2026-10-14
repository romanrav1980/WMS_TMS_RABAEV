from pathlib import Path
import json
f={}
p=Path("admin/wms_admin_frontend/src/features/finance/VehiclePhysicalProfile.tsx");s=p.read_text(encoding="utf-8")
s=s.replace('import {apiFetch','import "./VehiclePhysicalProfile.css";\nimport {apiFetch')
s=s.replace('<section aria-label="Физический класс автомобиля">','<section className="vehicle-profile-card" aria-label="Физический класс автомобиля">')
s=s.replace('<p role="status">','<p className="vehicle-profile-status" role="status">')
f[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/finance/VehicleFleetActions.tsx");s=p.read_text(encoding="utf-8").replace('Настроить класс и габариты грузового отсека этого автомобиля','Настроить класс, габариты и температурные возможности автомобиля').replace('>Габариты</button>','>Профиль</button>');f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");f[str(p)]=p.read_text(encoding="utf-8").replace("customer-orders.js?v=20261013-1141","customer-orders.js?v=20261014-1154")
print(json.dumps(f))
