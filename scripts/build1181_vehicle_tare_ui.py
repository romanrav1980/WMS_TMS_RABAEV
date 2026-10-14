from pathlib import Path
import json
f={}
p=Path("admin/wms_admin_frontend/src/features/finance/VehiclePhysicalProfile.tsx");s=p.read_text(encoding="utf-8")
s=s.replace('import "./VehiclePhysicalProfile.css";','import "./VehiclePhysicalProfile.css";\nimport {VehicleTareVariants,type FloorVariant,type TareType} from "./VehicleTareVariants";',1)
s=s.replace("measurement_verified:false}}};","measurement_verified:false};floor_capacity?:{variants:FloorVariant[];basis:string;evidence_reference:string}}};",1)
s=s.replace("temp_min_c?:string;temp_max_c?:string};","temp_min_c?:string;temp_max_c?:string;floor_variants?:FloorVariant[]};",1)
point=' const [fields,setFields]'
assert point in s;s=s.replace(point,' const [variants,setVariants]=useState<FloorVariant[]>([]),[tareTypes,setTareTypes]=useState<TareType[]>([]);\n'+point,1)
s=s.replace('  setProfile(null);setMessage("");setPending(null);setBlocked(false);','  setProfile(null);setMessage("");setPending(null);setBlocked(false);setVariants([]);setTareTypes([]);',1)
old='  const value=await apiFetch<Profile>("/api/admin/transport/vehicles/"+vehicle+"/profile");'
new='  const [value,types]=await Promise.all([apiFetch<Profile>("/api/admin/transport/vehicles/"+vehicle+"/profile"),apiFetch<TareType[]>("/api/admin/transport/vehicle-profiles/tare-types")]);'
assert old in s;s=s.replace(old,new,1)
s=s.replace('if(current.current===scope){setProfile(value);setFields','if(current.current===scope){setProfile(value);setTareTypes(types);setVariants(value.profile?.floor_capacity?.variants??[]);setFields',1)
point='  const intent:Pending={body:'
insert="""  if(variants.length>20||new Set(variants.map(v=>v.code)).size!==variants.length||variants.some(v=>! /^[A-Za-z0-9_.:-]{1,40}$/.test(v.code)||!v.limits.length||v.limits.length>8||new Set(v.limits.map(l=>l.pallet_type_id)).size!==v.limits.length||v.limits.some(l=>!Number.isInteger(l.max_places)||l.max_places<1||l.max_places>1000||!tareTypes.some(t=>t.id===l.pallet_type_id)))){
   setMessage("Укажите разные коды вариантов и активные типы тары с целым количеством1–1000.");return;
  }
"""
assert point in s;s=s.replace(point,insert+point,1)
s=s.replace('...(hasTemperature?{temp_min_c:fields.temp_min_c,temp_max_c:fields.temp_max_c}:{})}};',
'...(hasTemperature?{temp_min_c:fields.temp_min_c,temp_max_c:fields.temp_max_c}:{}),...(variants.length?{floor_variants:variants}:{})}};',1)
point='   <button type="submit"'
assert point in s;s=s.replace(point,'   <VehicleTareVariants value={variants} types={tareTypes} onChange={setVariants}/>\n'+point,1)
s=s.replace('Класс, грузовой отсек и температурные возможности','Класс, грузовой отсек, температура и тара',1)
f[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/finance/VehiclePhysicalProfile.css");f[str(p)]=p.read_text(encoding="utf-8")+"""
.vehicle-tare-variants{grid-column:1/-1;padding:18px;border-radius:12px;background:#f5f8fc;border:1px solid #dbe5f0}
.vehicle-tare-variants h4{font-size:17px;margin:0 0 8px}.vehicle-tare-variants p{font-size:13px;line-height:1.6;color:#52647a}
.vehicle-tare-variant{padding:16px;margin:14px 0;border:1px solid #d2dfed;border-radius:10px;background:white}
.vehicle-tare-heading,.vehicle-tare-limit{display:grid;grid-template-columns:minmax(0,2fr) minmax(90px,1fr) auto;gap:12px;align-items:end;margin-bottom:12px}
.vehicle-tare-heading{grid-template-columns:1fr auto}.vehicle-tare-variants select{width:100%;min-height:42px;padding:8px;border:1px solid #c9d6e6;border-radius:8px;background:white;color:#172b45}
@media(max-width:680px){.vehicle-tare-heading,.vehicle-tare-limit{grid-template-columns:1fr}.vehicle-tare-variants{padding:12px}}
"""
print(json.dumps(f))
