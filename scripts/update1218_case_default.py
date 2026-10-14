import json
from pathlib import Path
path=Path("api/wms_api_server/app/services/case_pick_service.py")
text=path.read_text(encoding="utf-8")
old="nvl(rule.PALLET_TYPE_ID, v_euro_pallet_type_id) PALLET_TYPE_ID"
assert old in text;text=text.replace(old,"nvl(RRL_RECIPIENT_PALLET_POLICY.type_id(wo.CUSTOMER_ID,co.CUSTOMER_STORE_MAP_ID), v_euro_pallet_type_id) PALLET_TYPE_ID",1)
start=text.index("                  left join (",text.index("def ensure_wave_case_pick_tasks"))
end=text.index("                 where wo.PICK_WAVE_ID",start)
assert "RRL_CUSTOMER_PALLET_TYPE_RULE"in text[start:end]
text=text[:start]+text[end:]
print(json.dumps({str(path):text},ensure_ascii=True))
