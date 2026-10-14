from pathlib import Path
import json
out={}
for name,import_name,needle,replacement in [
 ("box_costs.py","enqueue","            return result","            enqueue(cur,'WAREHOUSE_COST_RECOGNIZED',op,result,'MONETARY_RECOGNITION')\n            return result"),
 ("expense_decisions.py","enqueue,expense_payload","        return result","        if phase=='FINANCE':\n            enqueue(cur,'EXTRA_EXPENSE_RECOGNIZED' if outcome=='APPROVE' else 'EXTRA_EXPENSE_REJECTED',op,expense_payload(cur,expense,result),'MONETARY_RECOGNITION' if outcome=='APPROVE' else 'NO_POSTING')\n        return result"),
 ("expense_allocation.py","enqueue","            return result","            enqueue(cur,'EXTRA_EXPENSE_ALLOCATED',op,result,'ALLOCATION_ONLY')\n            return result")]:
 p=Path("api/wms_api_server/app/modules/finance/infrastructure")/name;s=p.read_text(encoding="utf-8-sig")
 at=s.index("from .cost_access import require_warehouse")
 s=s[:at]+"from .finance_outbox import "+import_name+"\n"+s[at:]
 assert needle in s;s=s.replace(needle,replacement)
 out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
