from pathlib import Path
import json,re
out={};d=Path("db/migrations/2026-10-12_ni061_nested_onward")
for name in["001_hu_shipping.sql","002_next.sql","003_recovery_next.sql","005_recovery_guard.sql"]:
 p=d/name;s=p.read_text(encoding="utf-8")
 s=s.replace("order by LEGACY_SBORKA_PALLET_ID) loop","order by 1) loop").replace("v_bindingand","v_binding and")
 if name=="005_recovery_guard.sql":
  assert "declare v_kind"not in s
  s=re.sub(r"for each row\s+begin","for each row\ndeclare v_kind varchar2(80);n number;\nbegin",s,count=1)
 out[p.as_posix()]=s
p=Path("scripts/build312.py");s=p.read_text(encoding="utf-8")
s=s.replace('s=s.replace("for each row\\nbegin","for each row\\ndeclare v_kind varchar2(80);n number;\\nbegin",1)','import re\ns=re.sub(r"for each row\\s+begin","for each row\\ndeclare v_kind varchar2(80);n number;\\nbegin",s,count=1)')
s=s.replace('"resolved.BINDING_ID=v_binding"','"resolved.BINDING_ID=v_binding "').replace('"+needle,1)\n# First bounded','"+needle.replace("order by LEGACY_SBORKA_PALLET_ID","order by 1"),1)\n# First bounded')
out[p.as_posix()]=s
print(json.dumps(out))
