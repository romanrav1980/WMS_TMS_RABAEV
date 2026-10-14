from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/return_disposal.py");s=p.read_text(encoding="utf-8")
a=s.index("        (select json_object('supported'");b=s.index("        req.OPERATION_ID",a)
s=s[:a]+"""        (select json_arrayagg(json_object('system_code'value p.SYSTEM_CODE,'profile_code'value p.PROFILE_CODE,'profile_version'value p.PROFILE_VERSION,'scan_mode'value p.SCAN_MODE)order by p.SYSTEM_CODE,p.PROFILE_CODE returning clob)from RRL_SKU_RECEIPT_PROFILE p where p.ARTICUL=r.ARTICLE) MARKED_PROFILES_JSON,
        (select count(*)from RRL_WMS_RECEIPT_UNIT u where u.CURRENT_UID=r.UID_PALLET and u.CURRENT_CELL=x.CELL and u.STOCK_STATUS='AVAILABLE') PHYSICAL_UNIT_COUNT,
"""+s[b:]
s=s.replace('        for row in rows:row["marked_unit_control"]=read_oracle_json(row.get("marked_unit_control"))if row.get("marked_unit_control")else None',"""        for row in rows:
            profiles=read_oracle_json(row.pop("marked_profiles_json"))or []
            count=row.pop("physical_unit_count")
            row["marked_unit_control"]={"supported":all(p["scan_mode"]=="UNIT"for p in profiles),"physical_unit_count":count,"expected_scan_count":count*len(profiles),"profiles":profiles}if profiles else None""")
print(json.dumps({str(p):s},ensure_ascii=True))
