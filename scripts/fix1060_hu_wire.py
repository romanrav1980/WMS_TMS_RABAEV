from pathlib import Path
import json,hashlib
folder="db/migrations/2026-10-13_ni072_nested_hu_wait/";files={}
t=Path(folder+"011_hu_wait_fix.sql").read_text(encoding="utf-8")
needle="  wire.put('operation_id',p_operation);";assert t.count(needle)==1
files[folder+"012_hu_wire.sql"]=t.replace(needle,"  wire.put('contract_version',2);\n"+needle)
p=folder+"apply.sql";files[p]=Path(p).read_text(encoding="utf-8")+"@@012_hu_wire.sql\n"
p=folder+"checkpoint.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["state"]="APPLIED_VALID_WIRE_CORRECTION_PREPARED"
v["wire_correction"]="1060 native root strict requires contract_version2; trial failed before plans/stock, retained pack phase reused"
v["sha256"].update({p:hashlib.sha256(t.encode()).hexdigest()for p,t in files.items()});files[p]=json.dumps(v,indent=2)
p="wiki/database/nicora_ni072_nested_hu_wait_20261013.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n1060: helper compilation now Errors[]Invalid[]. Retained source1057 packed bothCASE inoneHU via existingrepack afterclock1059 fix and canonical0.75 measurement. First plan trial rejected missing contract_version2 before newWHT orstock; explicit012wire correction checkpointed. Continue PACKED phase, no source rebirth.\n"
p="wiki/log.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n- checkpoint1060: helperVALID after011; retained1057 PACKED/P20H20, initialHU plan trial lacked strict Rootcontractversion2 (no WHT commit). Correction012 prepared, original request shapes retained.\n"
p="wiki/index.md";files[p]="- [Wire1060](database/nicora_ni072_nested_hu_wait_20261013.md): helperVALID, packedretainedsource, Rootcontractversion correction012 before trialretry.\n"+Path(p).read_text(encoding="utf-8")
print(json.dumps(files,ensure_ascii=True))
