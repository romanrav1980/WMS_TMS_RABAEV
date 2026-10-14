import json,re
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ..domain.historical_hu import departure_subtree","from ..domain.historical_hu import departure_subtree\nfrom ....transaction_gateway import TransactionGateway")
s=s.replace("    def preview(self, identifier: str) -> dict:","""    def preview(self, identifier: str, actor: str) -> dict:
        with self.gateway.transaction("Warehouse HU composition READ ONLY") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            bound = WarehouseHu(TransactionGateway(cur))
            data = bound._preview(identifier)
            assert_hu_view(cur, actor, int(data["warehouse"]))
            if data.get("case_task_id") is not None:
                cur.execute("select OPERATION_ID,PALLET_TYPE_ID,OWNER_WARE_ID from RRL_TARE_BOOK where PLACE_KIND='CASE'and PLACE_ID=:p_case and STATUS='HELD' fetch first 2 rows only",
                            p_case=str(data["case_task_id"]))
                books = cur.fetchall()
                if len(books) > 1:
                    raise HTTPException(409, "CASE_TARE_BOOK_AMBIGUOUS")
                data["tare_booking"] = ({"operation_id": books[0][0], "pallet_type_id": int(books[0][1]),
                                         "warehouse": int(books[0][2]), "nested_asset_preserved": True} if books else None)
            return data

    def _preview(self, identifier: str) -> dict:""")
s=s.replace("        result = json.loads(raw[0][\"snapshot\"])","        result = raw[0][\"snapshot\"] if isinstance(raw[0][\"snapshot\"], dict) else json.loads(raw[0][\"snapshot\"])")
s=s.replace("    def target_slots(self, cell: str, warehouse: int) -> list[dict]:","""    def target_slots(self, cell: str, warehouse: int, actor: str) -> list[dict]:
        with self.gateway.transaction("Warehouse HU target slots READ ONLY") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            assert_hu_view(cur, actor, warehouse)
            return WarehouseHu(TransactionGateway(cur))._target_slots(cell, warehouse)

    def _target_slots(self, cell: str, warehouse: int) -> list[dict]:""")
s+="""\n\ndef assert_hu_view(cur: Any, actor: str, warehouse: int) -> None:
    cur.execute("select WARE_ID,USER_GROUP,RRL_HAS_WRIGHT(ID,'warehouse_task_view') from RUSERS where ID=:p_actor and nvl(DELETED,0)=0", p_actor=actor)
    row = cur.fetchone()
    if row is None or row[2] != 1 or warehouse < 1 or (str(row[1] or "").strip().upper() != "GLOBAL_ADMIN" and row[0] != warehouse):
        raise HTTPException(403, "HU_CURRENT_WARE_VIEWER_REQUIRED")
"""
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/warehouse_hu_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace("def preview(self, identifier: str)","def preview(self, identifier: str, actor: str)").replace("def target_slots(self, cell: str, warehouse: int)","def target_slots(self, cell: str, warehouse: int, actor: str)")
s=s.replace("return service.preview(identifier)","return service.preview(identifier, _user.username)").replace("return service.target_slots(cell, warehouse)","return service.target_slots(cell, warehouse, _user.username)")
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-hus.js");s=p.read_text(encoding="utf-8")
s=s.replace('}else if(child.case_task_id){body.child_case_task_id=child.case_task_id;action+="-case";}', '''}else if(child.case_task_id){body.child_case_task_id=child.case_task_id;
            if(action==="attach"&&child.tare_booking)body.retained_tare_booking_operation_id=child.tare_booking.operation_id;
            action+="-case";}''')
s=s.replace('"; товарных листьев: "+data.leaf_count','"; товарных листьев: "+data.leaf_count')
out[str(p)]=s
for p in Path("scripts").glob("*.py"):
 s=p.read_text(encoding="utf-8-sig")
 if "hus=WarehouseHu(OracleGateway())"in s and re.search(r"hus\.preview\((parent|top|box)\)",s):
  s=re.sub(r"hus\.preview\((parent|top|box)\)",r'hus.preview(\1,"admin")',s);out[str(p)]=s
print(json.dumps(out))
