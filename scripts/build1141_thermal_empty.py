from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/shipping_temperature_read.py");s=p.read_text(encoding="utf-8")
s=s.replace("if not member_ids or len(member_ids)>5000","if len(member_ids)>5000",1)
needle='    cur.execute("""select /* CURRENT_ST_SKU_THERMAL1140 */'
early='''    if not member_ids:
        return {"basis":"CURRENT_WAREHOUSE_SKU_RULE","items":[],"common_min_c":None,"common_max_c":None,
                "ranges_conflict":False,"all_ranges_configured":False,"vehicle_temperature_verified":False,
                "sensor_temperature_verified":False,"operational_admission":False}
'''
s=s.replace(needle,early+needle,1)
p2=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js");t=p2.read_text(encoding="utf-8").replace('Температурные диапазоны части товаров не настроены; это не означает отсутствие требований.','Температурные требования части товаров не подтверждены: настройка отсутствует или некорректна.')
p3=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");u=p3.read_text(encoding="utf-8").replace('customer-orders.js?v=20261013-1133','customer-orders.js?v=20261013-1141')
print(json.dumps({str(p):s,str(p2):t,str(p3):u},ensure_ascii=True))
