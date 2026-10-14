from pathlib import Path
import json,sys
saved=json.loads(Path("tmp/progress499.json").read_text(encoding="utf-8"))
sys.argv=["resume500_finance_source.py",saved["tag"]]
source=Path("scripts/source499_aware_small_case.py").read_text(encoding="utf-8")
source="\n".join(line for line in source.splitlines()if not line.startswith('if Path("tmp/context499.json")')and not line.startswith('Path("tmp/progress499.json").write_text'))
# No goods/warehouse stage was entered when the restart interrupted policy PUT.
start=source.index(' call("PUT",f"/api/finished-goods/skus/{article}/receiving-policy"')
end=source.index("\n",start)
line=source[start:end]
source=source[:start]+''' q.execute("select count(*)from RRL_WARES where ID=:p_ware",p_ware=ware);assert q.fetchone()[0]==0,"Resume only before warehouse/goods creation"
 q.execute("select POLICY_VERSION from RRL_SKU_RECEIPT_POLICY where ARTICUL=:p_a",p_a=article);current_policy=q.fetchone()
 if current_policy is None or current_policy[0]==0:
 '''+line+'''
 else:assert current_policy[0]==1
'''+source[end:]
exec(compile(source,"source499_retained_resume","exec"))
