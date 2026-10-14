from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/quality_identifier.py");s=p.read_text(encoding="utf-8")
start=s.index('    cur.execute("""select distinct s.PALLET_UID')
end=s.index('    identifiers =',start)
s=s[:start]+'''    cur.execute("""select distinct PALLET_UID from (
        select s.PALLET_UID from RRL_SBORKA_PALLETS s where s.PALLET_UID=:p_code
        union all select s.PALLET_UID from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS s
        on s.ID=c.LEGACY_SBORKA_PALLET_ID where c.SSCC=:p_code
        union all select s.PALLET_UID from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS s
        on s.ID=c.LEGACY_SBORKA_PALLET_ID where c.CASE_PICK_TASK_ID=:p_case)
        fetch first 3 rows only""", p_code=value, p_case=case_id)
'''+s[end:]
print(json.dumps({str(p):s},ensure_ascii=True))
