from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/finance/infrastructure/shipping_register.py");v=p.read_text(encoding="utf-8")
a="where p.WARE_ID=:ware and p.ID>:after_id and p.STDATE is null and t.SHIPMENT_DATE>=:business_day and t.SHIPMENT_DATE<:day_end),"
b="""where p.WARE_ID=:ware and p.ID>:after_id and p.STDATE is null and t.SHIPMENT_DATE>=:business_day and t.SHIPMENT_DATE<:day_end
        union
        select p.ID from RRL_ST_DEFER_DECISION d join RRL_SBORKA_PALLETS p
          on p.ST_NUMBER=d.ST_NUMBER and p.WARE_ID=d.WARE_ID
        where d.WARE_ID=:ware and p.ID>:after_id and p.STDATE is null
          and json_value(d.RESULT_JSON,'$.original_shipping_date'returning varchar2(10))=:original_day),"""
assert a in v;v=v.replace(a,b)
a="ware=ware,after_id=after,business_day=day,day_end=day+timedelta(days=1),page_limit=limit+1)"
b="ware=ware,after_id=after,business_day=day,day_end=day+timedelta(days=1),original_day=day.isoformat(),page_limit=limit+1)"
assert a in v;v=v.replace(a,b)
v=v.replace('"member_scope":"EXACT_ST_BUSINESS_DATE"','"member_scope":"CURRENT_ST_OR_ORIGINAL_DEFERRED_TRIP_BUSINESS_DATE"')
print(json.dumps({str(p):v},ensure_ascii=True))
