from typing import Any

from ..oracle_gateway import OracleGateway
from ..schemas import WarehouseSettingsUpdateRequest


class WarehouseService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_warehouses(
        self,
        role: str | None = None,
        mes_enabled: int | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if role:
            role_column = role_to_column(role)
            if role_column:
                conditions.append(f"nvl({role_column}, 0) = 1")
        if mes_enabled is not None:
            conditions.append("nvl(MES_ENABLED, 0) = :mes_enabled")
            params["mes_enabled"] = 1 if int(mes_enabled) == 1 else 0
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        # C-0169: the same filtered/ordered/limited warehouse set first; cells and remains are aggregated only for that set and
        # left-joined (was three correlated subqueries per row: ~460 ms for all warehouses, now ~50 ms; small filtered sets ~8 -> ~25 ms).
        return self.gateway.fetch_all(
            f"""
            with sel as (
                select *
                  from (
                    select ID,
                           NAME,
                           PREFIX,
                           nvl(FLAG_RAW_MATERIAL, 0) FLAG_RAW_MATERIAL,
                           nvl(FLAG_PRODUCTION, 0) FLAG_PRODUCTION,
                           nvl(FLAG_PRODUCTION_BUFFER, 0) FLAG_PRODUCTION_BUFFER,
                           nvl(FLAG_FINISHED_GOODS, 0) FLAG_FINISHED_GOODS,
                           nvl(MES_ENABLED, 0) MES_ENABLED,
                           DEFAULT_RECEIVE_CELL,
                           DEFAULT_ISSUE_CELL,
                           WARE_COMMENT,
                           OVERFLOW_CELL_NAME,
                           PARENT_WARE_ID,
                           ORD2
                      from RRL_WARES w
                      {where_sql}
                     order by nvl(ORD2, ID), ID
                  )
                 where rownum <= :limit
            ),
            cc as (select c.WARE_ID, count(*) CELL_COUNT from RRL_CELLS c where c.WARE_ID in (select ID from sel) group by c.WARE_ID),
            st as (select c.WARE_ID, count(distinct r.UID_POLETA) PALLET_COUNT, sum(r.REMAIN) TOTAL_REMAIN
                     from RRL_REMAINS r
                     join RRL_CELLS c on c.CELL = r.CELL
                    where c.WARE_ID in (select ID from sel)
                    group by c.WARE_ID)
            select sel.*,
                   nvl(cc.CELL_COUNT, 0) CELL_COUNT,
                   nvl(st.PALLET_COUNT, 0) PALLET_COUNT,
                   nvl(st.TOTAL_REMAIN, 0) TOTAL_REMAIN
              from sel
              left join cc on cc.WARE_ID = sel.ID
              left join st on st.WARE_ID = sel.ID
             order by nvl(sel.ORD2, sel.ID), sel.ID
            """,
            params,
        )

    def update_warehouse(self, ware_id: int, request: WarehouseSettingsUpdateRequest) -> int:
        return self.gateway.execute(
            """
            update RRL_WARES
               set FLAG_RAW_MATERIAL = nvl(:flag_raw_material, FLAG_RAW_MATERIAL),
                   FLAG_PRODUCTION = nvl(:flag_production, FLAG_PRODUCTION),
                   FLAG_PRODUCTION_BUFFER = nvl(:flag_production_buffer, FLAG_PRODUCTION_BUFFER),
                   FLAG_FINISHED_GOODS = nvl(:flag_finished_goods, FLAG_FINISHED_GOODS),
                   MES_ENABLED = nvl(:mes_enabled, MES_ENABLED),
                   DEFAULT_RECEIVE_CELL = nvl(:default_receive_cell, DEFAULT_RECEIVE_CELL),
                   DEFAULT_ISSUE_CELL = nvl(:default_issue_cell, DEFAULT_ISSUE_CELL),
                   WARE_COMMENT = nvl(:ware_comment, WARE_COMMENT)
             where ID = :ware_id
            """,
            {"ware_id": ware_id, **_model_dict(request)},
        )


def _model_dict(model) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def role_to_column(role: str) -> str | None:
    return {
        "RAW_MATERIAL": "FLAG_RAW_MATERIAL",
        "PRODUCTION": "FLAG_PRODUCTION",
        "PRODUCTION_BUFFER": "FLAG_PRODUCTION_BUFFER",
        "FINISHED_GOODS": "FLAG_FINISHED_GOODS",
    }.get(role.upper())
