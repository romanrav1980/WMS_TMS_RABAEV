from pathlib import Path
import json
p="api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py";v=Path(p).read_text(encoding="utf-8")
needle="        normalized = normalize_incoming_sscc(identifier)";assert v.count(needle)==1
v=v.replace(needle,needle+'''
        case_number = identifier[5:] if identifier.startswith("CASE:") else ""
        case_id = (int(case_number) if case_number.isascii() and case_number.isdigit()
                   and len(case_number) <= 18 and str(int(case_number)) == case_number else None)''',1)
v=v.replace("where SSCC in(:p_code,:p_normal) fetch first 3 rows only","where SSCC in(:p_code,:p_normal) or CASE_PICK_TASK_ID=:p_case_id fetch first 3 rows only",1)
v=v.replace('{"p_code": identifier, "p_normal": normalized})','{"p_code": identifier, "p_normal": normalized, "p_case_id": case_id})',1)
print(json.dumps({p:v},ensure_ascii=True))
