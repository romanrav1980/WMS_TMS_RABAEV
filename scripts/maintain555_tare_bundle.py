import json
from pathlib import Path
out={}
p=Path("db/migrations/2026-10-12_ni063_damage_custody/001_schema.sql");v=p.read_text(encoding="utf-8")
assert v.startswith("create table"),"One-time schema conversion already done"
statements=[x.strip()for x in v.split(";")if x.strip()]
out[str(p)]="\n".join("begin execute immediate q'["+x+"]';exception when others then if sqlcode!=-955 then raise;end if;end;\n/\n"for x in statements)
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));name="../2026-10-12_ni063_damage_custody/apply.sql"
assert name not in m["additional_scripts"];m["additional_scripts"].append(name);out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki-raw/wms_admin_ui_reference/tare-ledger.js");v=p.read_text(encoding="utf-8")
v=v.replace('"tareOfferQty","tareOfferScan","tareAcceptQty"','"tareOfferQty","tareDamageOrigin","tareOfferScan","tareAcceptQty"')
v=v.replace('function resetData(){clearBookings();','function resetData(){el("tareDamageOrigin").value="";clearBookings();')
v=v.replace('el("tareWare").addEventListener("change",()=>{clearBookings();','el("tareWare").addEventListener("change",()=>{el("tareDamageOrigin").value="";clearBookings();')
v=v.replace('window.addEventListener("wms-admin-auth-ready",changed);changed();','el("tareCondition").addEventListener("change",()=>{el("tareDamageOrigin").value="";});el("tareType").addEventListener("change",()=>{el("tareDamageOrigin").value="";});window.addEventListener("wms-admin-auth-ready",changed);changed();')
out[str(p)]=v
p=Path("wiki-raw/wms_admin_ui_reference/tare-resolutions.js");v=p.read_text(encoding="utf-8").replace(' · доступное связанное количество ',' · связанное количество ');out[str(p)]=v
print(json.dumps(out))
