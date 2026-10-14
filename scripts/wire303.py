from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/delivery/domain/order_delivery.py");s=p.read_text(encoding="utf-8")
s=s.replace("from typing import Any","from typing import Any\nfrom .receipt_totals import combine_receipts",1)
start=s.index("    by_load_uid=");end=s.index("    grouped:",start)
s=s[:start]+'''    by_load_uid:dict[tuple[str,str],list[dict[str,Any]]]=defaultdict(list)
    for row in receipts:
        by_load_uid[(row["load_operation_id"],row.get("original_lot_uid",row["lot_uid"]))].append(row)
'''+s[end:]
s=s.replace('"unattributed","confirmed_transport_shortage")','"unattributed","confirmed_transport_shortage","historical_transport_shortage","recovered_transport_quantity")',1)
a=s.index('        transport_short=');b=s.index('        owners=',a)
s=s[:a]+'''        combined=combine_receipts(receipt,total)
        open_cases.update(combined["open_case_ids"])
'''+s[b:]
s=s.replace('counter["confirmed_transport_shortage"]+=transport_short\n            counter["unreceived"]+=transport_short','''counter["confirmed_transport_shortage"]+=combined["confirmed_transport_shortage"]
            counter["historical_transport_shortage"]+=combined["historical_transport_shortage"]
            counter["recovered_transport_quantity"]+=combined["recovered_transport_quantity"]
            counter["unreceived"]+=combined["unreceived"]''',1)
s=s.replace('counter[field]+=Decimal(receipt[field])','counter[field]+=combined[field]',1).replace('elif Decimal(receipt["accepted"])==total:','elif combined["accepted"]==total:',1)
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py");s=p.read_text(encoding="utf-8")
s=s.replace("import json","import json\nfrom pathlib import Path",1)
a=s.index('        q.execute("""',s.index("    def _receipts("));b=s.index('        result=rows(q)',a)
s=s[:a]+'''        q.execute(Path(__file__).with_name("order_delivery_receipts.sql").read_text(encoding="utf-8"),{"loads":json.dumps(loads)})
'''+s[b:]
s=s.replace('"confirmed_transport_shortage":row.get("confirmed_transport_shortage","0")','"historical_transport_shortage":row.get("confirmed_transport_shortage","0"),"recovered_transport_quantity":row.get("recovered_transport_quantity","0"),"is_corrective_receipt":bool(row.get("is_corrective_receipt",False))',1)
out[p.as_posix()]=s
print(json.dumps(out))
