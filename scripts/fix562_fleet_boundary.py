import json
from pathlib import Path
out={}
p=Path("admin/wms_admin_frontend/src/features/finance/index.ts");v=p.read_text(encoding="utf-8")
assert "VehiclePhysicalProfile"not in v
out[str(p)]=v+'export {VehiclePhysicalProfile} from "./VehiclePhysicalProfile";\nexport {VehicleFleetActions} from "./VehicleFleetActions";\n'
p=Path("admin/wms_admin_frontend/src/components/FleetManagementPage.tsx");v=p.read_text(encoding="utf-8")
v=v.replace('import {VehiclePhysicalProfile} from "../features/finance/VehiclePhysicalProfile";','import {VehiclePhysicalProfile,VehicleFleetActions} from "../features/finance";')
v=v.replace('function VehiclesTab() {\n  const [physicalVehicle,setPhysicalVehicle]=useState<number|null>(null);','function VehiclesTab({onPhysicalProfile}:{onPhysicalProfile:(vehicle:number)=>void}) {')
v=v.replace('export function FleetManagementPage({ onBack }: { onBack: () => void }) {','export function FleetManagementPage({ onBack }: { onBack: () => void }) {\n  const [physicalVehicle,setPhysicalVehicle]=useState<number|null>(null);')
v=v.replace('<VehiclesTab />','<VehiclesTab onPhysicalProfile={setPhysicalVehicle}/>')
physical='      {physicalVehicle!==null&&<VehiclePhysicalProfile key={physicalVehicle} vehicle={physicalVehicle} onClose={()=>setPhysicalVehicle(null)}/>}\n'
assert v.count(physical)==1;v=v.replace(physical,'')
target='<div className="fleet-tabs">';assert v.count(target)==1
v=v.replace(target,physical.strip()+'\n      '+target)
a="""              <td className="fleet-actions">
                <button className="fleet-edit-btn" onClick={() => openEdit(v)}>✏</button>
                <button type="button" title="Настроить класс и габариты грузового отсека этого автомобиля" onClick={()=>setPhysicalVehicle(v.ID)}>Габариты</button>
                <button className="fleet-del-btn" onClick={() => handleDelete(v.ID, v.NUM_PLAT)}>✕</button>
              </td>"""
assert v.count(a)==1
v=v.replace(a,'              <td className="fleet-actions"><VehicleFleetActions onEdit={()=>openEdit(v)} onDelete={()=>handleDelete(v.ID,v.NUM_PLAT)} onProfile={()=>onPhysicalProfile(v.ID)}/></td>')
out[str(p)]=v
print(json.dumps(out))
