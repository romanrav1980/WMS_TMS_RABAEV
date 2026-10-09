import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/case_shipment_binding.py")
s=p.read_text(encoding="utf-8")
s=s.replace("from .metadata_transactions import receipt_task_metadata","from .metadata_transactions import receipt_task_metadata\nfrom ..domain.carrier_shipment import assert_matching_composition",1)
needle='        shipment = cur.fetchone()\n        if not shipment:'
s=s.replace(needle,'        shipments = cur.fetchall()\n        if len(shipments) > 1:\n            raise ValueError("ST pallet identifier is ambiguous")\n        shipment = shipments[0] if shipments else None\n        if not shipment:',1)
needle='        cur.execute("update RRL_CASE_PICK_TASK set LEGACY_SBORKA_PALLET_ID=:sid,"'
assert s.count(needle)==1
guard="""        cur.execute("select p.ARTICUL,s.BASE_UOM,to_char(s.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') "
                    "from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID "
                    "join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID "
                    "where h.CASE_PICK_TASK_ID=:id and s.REMAIN>0 "
                    "order by h.LOT_UID,s.CELL fetch first 201 rows only", {"id": task_id})
        physical = cur.fetchall()
        cur.execute("select r.ARTICUL,to_char(r.QUANTITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),"
                    "u.BASE_UOM,u.NUMERATOR,u.DENOMINATOR,u.BASE_SCALE "
                    "from RRL_SBORKA_PALLET_ROWS r left join RRL_STOCK_UOM_CONVERSION u "
                    "on u.ARTICUL=r.ARTICUL and u.INPUT_UOM=r.EI and u.POLICY_VERSION="
                    "(select max(p.POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION p "
                    "where p.ARTICUL=r.ARTICUL and p.INPUT_UOM=r.EI) "
                    "where r.PALLET_UID=:uid order by r.ID fetch first 201 rows only",
                    {"uid": pallet_identifier})
        assert_matching_composition(physical, cur.fetchall())
"""
s=s.replace(needle,guard+needle,1)
out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/068_shipping.sql");s=p.read_text(encoding="utf-8")
needle="    if ct.LEGACY_SBORKA_PALLET_ID is null or ct.LEGACY_SBORKA_PALLET_ID!=v_id or ct.CUSTOMER_ORDER_ID!=v.get_number('customer_order_id')"
s=s.replace(needle,needle+"\n     or ct.WARE_ID is null or ct.WARE_ID!=v.get_number('warehouse')",1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
