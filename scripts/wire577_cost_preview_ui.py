from pathlib import Path
p=Path("admin/wms_admin_frontend/src/features/finance/TransportTariffSources.tsx");v=p.read_text(encoding="utf-8")
assert "TransportCostPreview"not in v
v='import {TransportCostPreview} from "./TransportCostPreview";\n'+v
anchor='   {current.candidates.map((r,i)=><TransportNormHistory'
assert anchor in v
v=v.replace(anchor,'   {current.candidates.map((r,i)=><TransportCostPreview key={warehouse+":"+r.id+":"+i} warehouse={warehouse} trip={trip} source={r.id}/>)}\n'+anchor)
p.write_text(v,encoding="utf-8")
p=Path("admin/wms_admin_frontend/src/features/finance/TransportNormHistory.tsx");v=p.read_text(encoding="utf-8")
anchor='{r.norm.vehicle_size_class}; тележка'
assert anchor in v
v=v.replace(anchor,'{r.norm.vehicle_size_class}; {r.norm.unload_charge_basis==="PLACE"?"за место":r.norm.unload_charge_basis==="POINT"?"за адрес":"единица не задана"}; паллета {r.norm.pallet_unload_rate??"не задано"}; тележка')
p.write_text(v,encoding="utf-8")
