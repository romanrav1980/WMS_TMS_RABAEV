from typing import Any

from ..oracle_gateway import OracleGateway
from ..schemas import ProductShipmentSettingsUpdateRequest


class ProductService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_shipment_settings(
        self,
        articul_like: str | None = None,
        only_with_aging: int | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if articul_like:
            conditions.append("(upper(ACTICUL) like :articul_like or upper(NAME) like :articul_like)")
            params["articul_like"] = f"%{articul_like.upper()}%"
        if only_with_aging is not None and int(only_with_aging) == 1:
            conditions.append("nvl(SHIPMENT_AGING_HOURS, 0) > 0")
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select ACTICUL,
                       NAME,
                       UNIT_TYPE,
                       nvl(SHIPMENT_AGING_HOURS, 0) SHIPMENT_AGING_HOURS,
                       SHIPMENT_AGING_COMMENT
                  from RRL_ARTICULS
                  {where_sql}
                 order by ACTICUL
              )
             where rownum <= :limit
            """,
            params,
        )

    def update_shipment_settings(
        self,
        articul: str,
        request: ProductShipmentSettingsUpdateRequest,
    ) -> int:
        return self.gateway.execute(
            """
            update RRL_ARTICULS
               set SHIPMENT_AGING_HOURS = nvl(:shipment_aging_hours, SHIPMENT_AGING_HOURS),
                   SHIPMENT_AGING_COMMENT = nvl(:shipment_aging_comment, SHIPMENT_AGING_COMMENT)
             where upper(ACTICUL) = upper(:articul)
            """,
            {
                "articul": articul,
                "shipment_aging_hours": request.shipment_aging_hours,
                "shipment_aging_comment": request.shipment_aging_comment,
            },
        )
