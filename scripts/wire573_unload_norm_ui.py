import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");v=p.read_text(encoding="utf-8")
v=v.replace("from typing import Any","from typing import Any,Literal",1)
a='    vehicle_size_class: str=Field(strict=True,min_length=1,max_length=40)';assert v.count(a)==1
v=v.replace(a,a+'\n    unload_charge_basis: Literal["POINT","PLACE"]|None=None\n    pallet_unload_rate: str|None=Field(default=None,strict=True,pattern=r"^[0-9]{1,18}(\\.[0-9]{1,9})?$")')
a='service.publish_transport_norm(body.model_dump(mode="json"),user.username)';assert v.count(a)==1
v=v.replace(a,'service.publish_transport_norm(body.model_dump(mode="json",exclude_none=True),user.username)')
out[str(p)]=v
p=Path("admin/wms_admin_frontend/src/features/finance/TransportNormPublisher.tsx");v=p.read_text(encoding="utf-8")
v=v.replace('export type TransportNorm={source:', 'export type TransportNorm={unload_charge_basis?:"POINT"|"PLACE";pallet_unload_rate?:string;source:')
v=v.replace('type Fields={currency:', 'type Fields={unload_charge_basis:string;pallet_unload_rate:string;currency:')
v=v.replace('const labels:Record<keyof Fields,string>={currency:', 'const labels:Record<keyof Fields,string>={unload_charge_basis:"Единица начисления выгрузки",pallet_unload_rate:"Выгрузка паллеты",currency:')
v=v.replace('useState<Fields>({currency:', 'useState<Fields>({unload_charge_basis:"",pallet_unload_rate:"",currency:')
v=v.replace('setFields({currency:', 'setFields({unload_charge_basis:norm?.unload_charge_basis||"",pallet_unload_rate:norm?.pallet_unload_rate||"",currency:')
v=v.replace('Object.keys(labels).some(k=>typeof b[k as keyof Fields]!=="string")', 'Object.keys(labels).filter(k=>k!=="unload_charge_basis"&&k!=="pallet_unload_rate").some(k=>typeof b[k as keyof Fields]!=="string")')
v=v.replace('if(!/^[A-Z]{3}$/.test(fields.currency)||!', 'if(!["POINT","PLACE"].includes(fields.unload_charge_basis)||!/^[A-Z]{3}$/.test(fields.currency)||!')
v=v.replace('[fields.rolling_unload_rate,fields.manual_unload_rate,fields.loader_rate]', '[fields.rolling_unload_rate,fields.manual_unload_rate,fields.loader_rate,fields.pallet_unload_rate]')
a='<input required type={k==="effective_from"?"date":"text"}';assert v.count(a)==1
v=v.replace(a,'{k==="unload_charge_basis"?<select required title="Выберите начисление один раз за адрес или за каждое физическое место" value={fields[k]} onChange={e=>setFields(v=>({...v,[k]:e.target.value}))}><option value="">Выберите единицу</option><option value="POINT">За обслуженный адрес</option><option value="PLACE">За физическое место</option></select>:<input required type={k==="effective_from"?"date":"text"}')
a='onChange={e=>setFields(v=>({...v,[k]:e.target.value}))}/></label>)}';assert v.count(a)==1
v=v.replace(a,'onChange={e=>setFields(v=>({...v,[k]:e.target.value}))}/>}</label>)}')
out[str(p)]=v
p=Path("admin/wms_admin_frontend/src/features/finance/TransportTariffSources.tsx");v=p.read_text(encoding="utf-8")
a='Выгрузка тележки {r.published_norm.rolling_unload_rate},';assert v.count(a)==1
v=v.replace(a,'Начисление {r.published_norm.unload_charge_basis==="POINT"?"за адрес":r.published_norm.unload_charge_basis==="PLACE"?"за место":"не настроено"}, паллетой {r.published_norm.pallet_unload_rate??"не задано"}. Выгрузка тележки {r.published_norm.rolling_unload_rate},')
out[str(p)]=v
print(json.dumps(out))
