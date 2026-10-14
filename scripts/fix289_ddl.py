from pathlib import Path
import json
out={};base=Path("db/migrations/2026-10-11_ni062_reuse_approval")
p=base/"001_reuse_helper.sql";s=p.read_text(encoding="utf-8");parts=s.split("CREATE OR REPLACE EDITIONABLE PACKAGE BODY")
assert len(parts)==3
out[p.as_posix()]=parts[0].rstrip()+"\n/\nCREATE OR REPLACE EDITIONABLE PACKAGE BODY"+parts[2]
p=base/"000_before_spec.sql";s=p.read_text(encoding="utf-8");out[p.as_posix()]=s.split("CREATE OR REPLACE EDITIONABLE PACKAGE BODY",1)[0].rstrip()+"\n/\n"
p=base/"002_command.sql";s=p.read_text(encoding="utf-8");s=s.replace("p_domain.put('reuse_source',reuse_source);\n end;","p_domain.put('reuse_source',reuse_source);\n end if;");out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
