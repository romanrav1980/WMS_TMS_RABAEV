import json
from pathlib import Path
p=Path("db/migrations/2026-10-12_ni062_return_basis/004_command.sql");s=p.read_text(encoding="utf-8")
marker="p_domain:=json_object_t();"
assert s.count(marker)==1
s=s.replace(marker,"if RRL_STOCK_QC_MARK.required_for_article(original.ARTICLE)=1 then v_units:=greatest(v_units,1);end if;\n "+marker)
print(json.dumps({str(p):s}))
