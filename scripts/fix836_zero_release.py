from pathlib import Path
import json,hashlib
p=Path("db/migrations/2026-10-13_ni032_sequential_sources/001_wave.sql")
s=p.read_text(encoding="utf-8")
s=s.replace("create or replace package body RRL_STOCK_WAVE_CMD as","""create or replace package body RRL_STOCK_WAVE_CMD as
 function release_amount(p_text varchar2)return number is
 begin
  if p_text='0'then return 0;end if;
  return RRL_STOCK_MATH.quantity(p_text);
 end;
""",1)
s=s.replace("RRL_STOCK_MATH.quantity(x.get_string('release_quantity'))","release_amount(x.get_string('release_quantity'))")
s=s.replace("RRL_STOCK_MATH.quantity(v_source.get_string('release_quantity'))","release_amount(v_source.get_string('release_quantity'))")
files={str(p):s}
p=Path("db/migrations/2026-10-13_ni032_sequential_sources/checkpoint.json")
v=json.loads(p.read_text(encoding="utf-8"));v.update(after_sha256=hashlib.sha256(s.encode()).hexdigest(),state="APPLIED_COMPILED_CASE835_ZERO_RELEASE_REJECTED_BEFORE_EFFECT_FIXED836")
files[str(p)]=json.dumps(v,indent=2)
p=Path("wiki/database/retailcase_ni032_sequential_sources_20261013.md")
files[str(p)]=p.read_text(encoding="utf-8")+"\n834 APPLIED/USER_ERRORS empty/INVALID empty before case. Fresh835 refused before rebind effect because canonical positive-only quantity parser received zero release; original root rolled back and finally cleaned own P/H.836 private release_amount admits only canonical generated0 and delegates positives to existing exact math. Reapply/fresh case pending; no acceptance claim.\n"
p=Path("wiki/log.md")
files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 fix836: applied834 VALID; fresh835 exposed positive-only zero-release parser before rebind, root rollback/own cleanup. Private canonical-zero helper836 prepared/SHA refreshed; positive parsing remains authoritative RRL_STOCK_MATH. Fresh case pending.\n"
print(json.dumps(files,ensure_ascii=True))
