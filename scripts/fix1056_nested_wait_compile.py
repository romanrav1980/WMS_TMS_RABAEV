from pathlib import Path
import json,hashlib
d="db/migrations/2026-10-13_ni072_nested_hu_wait/"
p=d+"003_hu_wait.sql";t=Path(p).read_text(encoding="utf-8")
assert "st_numberorder by" in t
fixed=t.replace("st_numberorder by","st_number order by")
files={d+"011_hu_wait_fix.sql":fixed}
p=d+"apply.sql";files[p]=Path(p).read_text(encoding="utf-8")+"@@011_hu_wait_fix.sql\n@@009_compile.sql\n"
p=d+"checkpoint.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["state"]="APPLIED_INITIAL_COMPILE_ERROR_CORRECTION_PREPARED";v["correction"]="1056 whitespace after scalar SQL replacement; no source operation executed"
v["sha256"].update({p:hashlib.sha256(t.encode()).hexdigest() for p,t in files.items()});files[p]=json.dumps(v,indent=2)
p="wiki/database/nicora_ni072_nested_hu_wait_20261013.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n1056: initial apply executed11statements, live verification found new HU helper body invalid because scalar replacement joined st_number/order tokens. Original003 retained as evidence; corrected011 before any newHU operation. Live recompile pending; not accepted.\n"
p="wiki/log.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n- checkpoint1056: nestedHU migration initial helpercompilefailed (missing separator in scalar query), no goods/plans executed. Paired original retained, correction011 checkpointed before live retry.\n"
p="wiki/index.md";files[p]="- [Correction1056](database/nicora_ni072_nested_hu_wait_20261013.md): newhelper compile separator fixed in011, runtime pending.\n"+Path(p).read_text(encoding="utf-8")
print(json.dumps(files,ensure_ascii=True))
