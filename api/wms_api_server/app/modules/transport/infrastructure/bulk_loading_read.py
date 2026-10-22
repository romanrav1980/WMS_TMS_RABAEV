"""Resolve a physical BOX or weighed CASE carton in one authorized snapshot."""
from typing import Any
from ...inventory.public import WarehouseHu
from ...platform.public import read_oracle_json
from ....transaction_gateway import TransactionGateway
from ..contracts import TransportLoadingError


def bulk_loading_preview(gateway: Any, identifier: str, actor: str) -> dict[str, Any]:
    with gateway.transaction("Current physical bulk BOX preview READ ONLY") as cur:
        cur.execute("set transaction read only")
        snapshot=WarehouseHu(TransactionGateway(cur)).preview(identifier,actor)
        if snapshot.get("historical_composition") or snapshot.get("ancestors"):
            raise TransportLoadingError("BULK_BOX_INDEPENDENT_REQUIRED","Сначала освободите короб из родительского места.")
        cur.execute("select RRL_ACCESS_API.allowed(:a,'stock_posting_shipping','WAREHOUSE',:w)from dual",a=actor,w=str(snapshot["warehouse"]))
        if cur.fetchone()[0]!=1:
            raise TransportLoadingError("BULK_BOX_SHIPPING_FORBIDDEN","Нет доступа к погрузке на этом складе.",status=403)
        root=snapshot["nodes"][0]
        if root["kind"]=="CONTAINER" and root.get("type")=="BOX":
            return dict(source_kind="HU",snapshot=snapshot,identifier=snapshot["root"])
        if root["kind"]=="CASE":
            cur.execute("""select sp.PALLET_UID from RRL_CASE_PICK_TASK ct
                join RRL_PALLET_TYPE pt on pt.PALLET_TYPE_ID=ct.PALLET_TYPE_ID
                join RRL_SBORKA_PALLETS sp on sp.ID=ct.LEGACY_SBORKA_PALLET_ID
                where ct.CASE_PICK_TASK_ID=:t and upper(pt.LOAD_UNIT_CLASS)='CONTAINER'
                and pt.FINAL_WEIGHT_REQUIRED=1 and pt.ACTIVE=1 and ct.SHIPPED_OPERATION is null""",t=root["case_task_id"])
            row=cur.fetchone()
            if row:
                cur.execute("select RRL_STOCK_LOADING_READ.preview_json(:id,:a)from dual",id=row[0],a=actor)
                value=read_oracle_json(cur.fetchone()[0])
                if value["snapshot"]["root"]!=snapshot["root"]:
                    raise TransportLoadingError("BULK_BOX_BINDING_CHANGED","Перечитайте состав короба.")
                return dict(value,source_kind="SINGLE",identifier=row[0])
        raise TransportLoadingError("BULK_BOX_REQUIRED","Сканируйте самостоятельный короб с настроенным весовым контролем.")
