import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");s=p.read_text(encoding="utf-8")
old='return {"trip_id":trip,"lines":self._lines("l.TT_ID=:id",trip,actor)}'
new='''from ..domain.cost_summary import recognized_cost_summary
        rows=self._lines("l.TT_ID=:id",trip,actor)
        try:
            return {"trip_id":trip,"lines":rows,"summary":recognized_cost_summary(rows)}
        except ValueError as exc:
            raise LogisticsCostError("COST_SUMMARY_SOURCE_INVALID",str(exc))from exc'''
assert s.count(old)==1;s=s.replace(old,new);out[str(p)]=s
p=Path("wiki/database/retailcase_ni071_revision_summary_20261012.md");s=p.read_text(encoding="utf-8")
s+="""
SQL506: fixed selector Python4.941ms/21 buffers; native2.179ms/6.7 buffers. Existing invoice/trip lines cold37.56–55.977ms with 76–145 buffers. Decision finance: preserve new dated-version index, 500-source bound and exact current WARE scope; one-query grouping in memory, no extra ORM N+1 or cross-currency aggregation. Owner finance: review invoice PAY_ORDER_ID / cost load join plans and batching if warm query remains over50ms or real invoice exceeds500 sources; no index added without plan evidence. Trip read now exposes same exact original-cost summary508.
"""
out[str(p)]=s
p=Path("wiki/index.md");s=p.read_text(encoding="utf-8").replace("scoped exact invoice groups.","scoped exact invoice/trip groups.");out[str(p)]=s
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n-12.10.2026 506–508: finance selector4.941/native2.179ms; invoice cold37.56–55.977ms bounded500, one-query in-memory grouping/WARE scope; plan+batch owner finance backlog thresholdwarm50ms/500sources. Trip read shares exact original summary.\n"
print(json.dumps(out))
