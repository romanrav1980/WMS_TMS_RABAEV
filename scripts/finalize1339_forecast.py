from pathlib import Path
import json
files={}
base=Path("db/migrations/2026-10-08_stock_posting_core");d=base/"../2026-10-14_ni081_forecast_norm_scope"
files[str(d/"005_current_api.sql")]=(d/"000_before_spec.sql").read_text(encoding="utf-8")+(d/"002_api.sql").read_text(encoding="utf-8")
p=base/"current_runtime_manifest.json";m=json.loads(p.read_text(encoding="utf-8"))
old="../2026-10-10_ni081_attendance_replace/001_api.sql";new="../2026-10-14_ni081_forecast_norm_scope/005_current_api.sql"
assert old in m["components"]or new in m["components"];m["components"]=[new if x==old else x for x in m["components"]]
for key,value in [("startup_scripts","../2026-10-14_ni081_forecast_norm_scope/001_schema.sql"),("additional_scripts","../2026-10-14_ni081_forecast_norm_scope/apply.sql")]:
 if value not in m[key]:m[key].append(value)
files[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-forecast-labour.js");s=p.read_text(encoding="utf-8")
s=s.replace(' function node(tag,text)', ' const quantity=v=>String(v).replace(/(\\.\\d*?)0+$/,"$1").replace(/\\.$/,"");\n function node(tag,text)')
s=s.replace('data.total_person_hours+" чел·ч"','quantity(data.total_person_hours)+" чел·ч"').replace('data.known_person_hours+" чел·ч;','quantity(data.known_person_hours)+" чел·ч;').replace('row.estimated_person_hours+" чел·ч"','quantity(row.estimated_person_hours)+" чел·ч"')
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-forecast.css");files[str(p)]=p.read_text(encoding="utf-8")+"\n.wf-page #wfLabourResult>p:first-child{font-size:24px;font-weight:700;color:#173a67;margin:12px 0}\n.wf-page #wfLabourResult details{border:1px solid #dce6f3;border-radius:10px;padding:14px;margin:10px 0;background:#f8fbff}\n.wf-page #wfLabourResult summary{font-weight:600;cursor:pointer;min-height:28px}\n"
p=Path("scripts/build1317_unload.py");files[str(p)]=p.read_text(encoding="utf-8").replace('"l.ROOT_UID=s.ROOT_KEY"','"l.ROOT_UID=s.ROOT_KEY "')
print(json.dumps(files,ensure_ascii=True))
