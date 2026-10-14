import json
from pathlib import Path
p=Path("admin/wms_admin_frontend/src/components/FleetManagementPage.tsx");v=p.read_text(encoding="utf-8")
assert "VehiclePhysicalProfile"not in v
v=v.replace('import { apiFetch } from "../api";','import { apiFetch } from "../api";\nimport {VehiclePhysicalProfile} from "../features/finance/VehiclePhysicalProfile";')
v=v.replace('function VehiclesTab() {','function VehiclesTab() {\n  const [physicalVehicle,setPhysicalVehicle]=useState<number|null>(null);')
a='<button className="fleet-edit-btn" onClick={() => openEdit(v)}>✏</button>';assert v.count(a)==1
v=v.replace(a,a+'\n                <button type="button" title="Настроить класс и габариты грузового отсека этого автомобиля" onClick={()=>setPhysicalVehicle(v.ID)}>Габариты</button>')
a='      {dialog && (';assert v.count(a)==2
v=v.replace(a,'      {physicalVehicle!==null&&<VehiclePhysicalProfile key={physicalVehicle} vehicle={physicalVehicle} onClose={()=>setPhysicalVehicle(null)}/>}\n'+a,1)
print(json.dumps({str(p):v}))
