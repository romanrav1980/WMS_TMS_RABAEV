import json,re
from pathlib import Path
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/142_metadata_fence.sql");s=p.read_text(encoding="utf-8").replace("'case_pick_short_approve')","'case_pick_short_approve','outgoing_pallet_edit')",1);out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/180_remains_adapter.sql");s=p.read_text(encoding="utf-8")
for name in ("trial_by_weight","set_scan_proove"):
 pattern=r"(function\s+"+name+r"\s*\()(.*?)(\)\s*return\s+int)"
 # spec and body have same declaration shape.
 s,n=re.subn(pattern,lambda m:m.group(1)+m.group(2)+",p_operation_id varchar2 default null"+m.group(3),s,count=2,flags=re.I|re.S)
 if n!=2:raise RuntimeError("Expected specification/body "+name)
s=s.replace("return RRL_TRIAL_BY_WEIGHT(PALLET_UID1, TRIAL_WEIGHT1, WOOD_WEIGHT1, user_id1);","return RRL_TRIAL_BY_WEIGHT(PALLET_UID1, TRIAL_WEIGHT1, WOOD_WEIGHT1, user_id1,p_operation_id);",1)
s=s.replace("return RRL_SET_SCAN_PROOVE2(PALLET_UID1, count_of_errors1, prim1, SBORSHIK1, KLADOVSHIK1);","return RRL_SET_SCAN_PROOVE2(PALLET_UID1, count_of_errors1, prim1, SBORSHIK1, KLADOVSHIK1,p_operation_id,KLADOVSHIK1);",1)
out[str(p)]=s
p=Path("WindowsApplication2/WindowsApplication2/Form1.cs");s=p.read_text(encoding="utf-8")
at=s.index('ora_com.CommandText = "REMAINS.TRIAL_BY_WEIGHT";');end=s.index("int rowsAffected = ora_com.ExecuteNonQuery();",at)
part=s[at:end]
part=part.replace("Convert.ToDouble(m_trial_weight.Text)","Decimal.Parse(m_trial_weight.Text)").replace("Convert.ToDouble(ВесДеревянногоПаллета.Text)","Decimal.Parse(ВесДеревянногоПаллета.Text)")
part+='StockCommandIntent qualityIntent = StockCommandIntent.Prepare(ora_com, wms_user.user_id, PUID);\n                '
s=s[:at]+part+s[end:]
needle="int rowsAffected = ora_com.ExecuteNonQuery();";pos=at+len(part);s=s[:pos]+s[pos:].replace(needle,needle+"\n                qualityIntent.Confirm();",1)
at=s.index('ora_com3.CommandText = "REMAINS.SET_SCAN_PROOVE";');end=s.index("int rowsAffected = ora_com3.ExecuteNonQuery();",at)
s=s[:end]+"StockCommandIntent scanIntent = StockCommandIntent.Prepare(ora_com3, wms_user.user_id, pallet_uid);\n            "+s[end:]
end=s.index("int rowsAffected = ora_com3.ExecuteNonQuery();",at)+len("int rowsAffected = ora_com3.ExecuteNonQuery();")
s=s[:end]+"\n            scanIntent.Confirm();"+s[end:]
out[str(p)]=s
m=json.loads(Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json").read_text(encoding="utf-8"))
for name in ("186_quality_native_legacy.sql","186_quality_native_calculations.sql","186_quality_native_entrypoints.sql"):
 if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
out["db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
