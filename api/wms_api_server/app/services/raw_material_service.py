from typing import Any

from ..oracle_gateway import OracleGateway
from ..schemas import RawMaterialSkuSettingsUpdateRequest


class RawMaterialService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_skus(
        self,
        search: str | None = None,
        only_active: int | None = 1,
        only_with_stock: int | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conditions = [
            """
            (
              nvl(s.IS_RAW_MATERIAL, 0) = 1
              or upper(a.ACTICUL) like 'RM-%'
              or exists (
                select 1
                  from RRL_PALLETS p
                  join RRL_REMAINS r on r.UID_POLETA = p.UID_PALLET
                  join RRL_CELLS c on c.CELL = r.CELL
                  join RRL_WARES w on w.ID = c.WARE_ID
                 where upper(p.ARTICUL) = upper(a.ACTICUL)
                   and nvl(w.FLAG_RAW_MATERIAL, 0) = 1
                   and nvl(r.REMAIN, 0) <> 0
              )
            )
            """
        ]
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if search:
            conditions.append("(upper(a.ACTICUL) like :search or upper(a.NAME) like :search)")
            params["search"] = f"%{search.upper()}%"
        if only_active is not None and int(only_active) == 1:
            conditions.append("nvl(s.ACTIVE, 1) = 1")
        if only_with_stock is not None and int(only_with_stock) == 1:
            conditions.append("nvl(st.TOTAL_REMAIN, 0) <> 0")
        where_sql = " where " + " and ".join(conditions)
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select a.ACTICUL ARTICUL,
                       a.NAME,
                       a.UNIT_TYPE,
                       a.CELL DEFAULT_CELL,
                       a.BESTBEFOREDAYS SHELF_LIFE_DAYS,
                       nvl(s.IS_RAW_MATERIAL, case when upper(a.ACTICUL) like 'RM-%' then 1 else 0 end) IS_RAW_MATERIAL,
                       s.RAW_GROUP,
                       nvl(s.MERCURY_REQUIRED, 0) MERCURY_REQUIRED,
                       nvl(s.LOT_REQUIRED, 1) LOT_REQUIRED,
                       nvl(s.EXPIRY_REQUIRED, 1) EXPIRY_REQUIRED,
                       s.MIN_STOCK_QTY,
                       s.TARGET_STOCK_QTY,
                       s.ALLOWED_WARE_IDS,
                       s.ALLOWED_ZONE_CODES,
                       s.TECHNOLOGIST_COMMENT,
                       nvl(s.ACTIVE, 1) ACTIVE,
                       nvl(st.TOTAL_REMAIN, 0) TOTAL_REMAIN,
                       nvl(st.PALLET_COUNT, 0) PALLET_COUNT,
                       nvl(st.WAREHOUSE_COUNT, 0) WAREHOUSE_COUNT,
                       st.NEAREST_EXPIRY_DATE
                  from RRL_ARTICULS a
                  left join RRL_RAW_MATERIAL_SKU s
                    on upper(s.ARTICUL) = upper(a.ACTICUL)
                  left join (
                    select upper(p.ARTICUL) ARTICUL,
                           sum(nvl(r.REMAIN, 0)) TOTAL_REMAIN,
                           count(distinct r.UID_POLETA) PALLET_COUNT,
                           count(distinct c.WARE_ID) WAREHOUSE_COUNT,
                           min(p.EXPIRY_DATE) NEAREST_EXPIRY_DATE
                      from RRL_PALLETS p
                      join RRL_REMAINS r on r.UID_POLETA = p.UID_PALLET
                      join RRL_CELLS c on c.CELL = r.CELL
                      join RRL_WARES w on w.ID = c.WARE_ID
                     where nvl(w.FLAG_RAW_MATERIAL, 0) = 1
                       and nvl(r.REMAIN, 0) <> 0
                     group by upper(p.ARTICUL)
                  ) st on st.ARTICUL = upper(a.ACTICUL)
                  {where_sql}
                 order by a.ACTICUL
              )
             where rownum <= :limit
            """,
            params,
        )

    def update_sku_settings(self, articul: str, request: RawMaterialSkuSettingsUpdateRequest) -> int:
        params = {"articul": articul, **_model_dict(request)}
        return self.gateway.execute(
            """
            merge into RRL_RAW_MATERIAL_SKU d
            using (
              select upper(substr(:articul, 1, 40)) ARTICUL,
                     :is_raw_material IS_RAW_MATERIAL,
                     :raw_group RAW_GROUP,
                     :mercury_required MERCURY_REQUIRED,
                     :lot_required LOT_REQUIRED,
                     :expiry_required EXPIRY_REQUIRED,
                     :min_stock_qty MIN_STOCK_QTY,
                     :target_stock_qty TARGET_STOCK_QTY,
                     :allowed_ware_ids ALLOWED_WARE_IDS,
                     :allowed_zone_codes ALLOWED_ZONE_CODES,
                     :technologist_comment TECHNOLOGIST_COMMENT,
                     :active ACTIVE,
                     :updated_by UPDATED_BY
                from dual
            ) s
            on (upper(d.ARTICUL) = s.ARTICUL)
            when matched then update set
              d.IS_RAW_MATERIAL = nvl(s.IS_RAW_MATERIAL, d.IS_RAW_MATERIAL),
              d.RAW_GROUP = nvl(s.RAW_GROUP, d.RAW_GROUP),
              d.MERCURY_REQUIRED = nvl(s.MERCURY_REQUIRED, d.MERCURY_REQUIRED),
              d.LOT_REQUIRED = nvl(s.LOT_REQUIRED, d.LOT_REQUIRED),
              d.EXPIRY_REQUIRED = nvl(s.EXPIRY_REQUIRED, d.EXPIRY_REQUIRED),
              d.MIN_STOCK_QTY = nvl(s.MIN_STOCK_QTY, d.MIN_STOCK_QTY),
              d.TARGET_STOCK_QTY = nvl(s.TARGET_STOCK_QTY, d.TARGET_STOCK_QTY),
              d.ALLOWED_WARE_IDS = nvl(s.ALLOWED_WARE_IDS, d.ALLOWED_WARE_IDS),
              d.ALLOWED_ZONE_CODES = nvl(s.ALLOWED_ZONE_CODES, d.ALLOWED_ZONE_CODES),
              d.TECHNOLOGIST_COMMENT = nvl(s.TECHNOLOGIST_COMMENT, d.TECHNOLOGIST_COMMENT),
              d.ACTIVE = nvl(s.ACTIVE, d.ACTIVE),
              d.UPDATED_BY = nvl(s.UPDATED_BY, d.UPDATED_BY),
              d.UPDATED_AT = systimestamp
            when not matched then insert (
              ARTICUL, IS_RAW_MATERIAL, RAW_GROUP, MERCURY_REQUIRED,
              LOT_REQUIRED, EXPIRY_REQUIRED, MIN_STOCK_QTY, TARGET_STOCK_QTY,
              ALLOWED_WARE_IDS, ALLOWED_ZONE_CODES, TECHNOLOGIST_COMMENT,
              ACTIVE, CREATED_BY, CREATED_AT, UPDATED_BY, UPDATED_AT
            ) values (
              s.ARTICUL, nvl(s.IS_RAW_MATERIAL, 1), s.RAW_GROUP, nvl(s.MERCURY_REQUIRED, 0),
              nvl(s.LOT_REQUIRED, 1), nvl(s.EXPIRY_REQUIRED, 1), s.MIN_STOCK_QTY, s.TARGET_STOCK_QTY,
              s.ALLOWED_WARE_IDS, s.ALLOWED_ZONE_CODES, s.TECHNOLOGIST_COMMENT,
              nvl(s.ACTIVE, 1), nvl(s.UPDATED_BY, 'API'), systimestamp, nvl(s.UPDATED_BY, 'API'), systimestamp
            )
            """,
            params,
        )

    def list_warehouses(self, limit: int = 200) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select *
              from (
                select w.ID,
                       w.NAME,
                       w.PREFIX,
                       nvl(w.MES_ENABLED, 0) MES_ENABLED,
                       w.DEFAULT_RECEIVE_CELL,
                       w.DEFAULT_ISSUE_CELL,
                       w.WARE_COMMENT,
                       count(distinct c.CELL) CELL_COUNT,
                       count(distinct r.UID_POLETA) PALLET_COUNT,
                       nvl(sum(r.REMAIN), 0) TOTAL_REMAIN,
                       count(distinct p.ARTICUL) SKU_COUNT
                  from RRL_WARES w
                  left join RRL_CELLS c on c.WARE_ID = w.ID
                  left join RRL_REMAINS r on r.CELL = c.CELL
                  left join RRL_PALLETS p on p.UID_PALLET = r.UID_POLETA
                 where nvl(w.FLAG_RAW_MATERIAL, 0) = 1
                 group by w.ID, w.NAME, w.PREFIX, w.MES_ENABLED,
                          w.DEFAULT_RECEIVE_CELL, w.DEFAULT_ISSUE_CELL, w.WARE_COMMENT
                 order by nvl(w.ID, 0)
              )
             where rownum <= :limit
            """,
            {"limit": min(max(limit, 1), 500)},
        )

    def list_remains(
        self,
        articul: str | None = None,
        ware_id: int | None = None,
        ware_ids: str | None = None,
        cell: str | None = None,
        batch_no: str | None = None,
        quality_status: str | None = None,
        only_available: int | None = 1,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        conditions = ["nvl(w.FLAG_RAW_MATERIAL, 0) = 1"]
        params: dict[str, Any] = {"limit": min(max(limit, 1), 1000)}
        if articul:
            conditions.append("upper(p.ARTICUL) like :articul")
            params["articul"] = f"%{articul.upper()}%"
        if ware_id is not None:
            conditions.append("w.ID = :ware_id")
            params["ware_id"] = int(ware_id)
        elif ware_ids:
            parsed_ware_ids = [
                int(value.strip())
                for value in ware_ids.split(",")
                if value.strip().isdigit()
            ][:100]
            if parsed_ware_ids:
                placeholders = []
                for idx, value in enumerate(parsed_ware_ids):
                    key = f"ware_id_{idx}"
                    placeholders.append(f":{key}")
                    params[key] = value
                conditions.append(f"w.ID in ({', '.join(placeholders)})")
        if cell:
            conditions.append("upper(r.CELL) like :cell")
            params["cell"] = f"%{cell.upper()}%"
        if batch_no:
            conditions.append("upper(nvl(rb.RAW_BATCH_NO, to_char(p.PRIHOD_NAKLAD_ID))) like :batch_no")
            params["batch_no"] = f"%{batch_no.upper()}%"
        if quality_status:
            conditions.append("upper(nvl(p.QUALITY_STATUS, 'UNKNOWN')) = :quality_status")
            params["quality_status"] = quality_status.upper()
        if only_available is not None and int(only_available) == 1:
            conditions.append("nvl(r.REMAIN, 0) > 0")
        where_sql = " where " + " and ".join(conditions)
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select w.ID WARE_ID,
                       w.NAME WARE_NAME,
                       r.CELL,
                       r.UID_POLETA UID_PALLET,
                       p.SSCC,
                       p.ARTICUL,
                       a.NAME ARTICUL_NAME,
                       a.UNIT_TYPE,
                       rb.RAW_BATCH_NO,
                       rb.MERCURY_VSD_UUID,
                       p.PRODUCED_DATE,
                       p.EXPIRY_DATE,
                       r.REMAIN QTY,
                       0 RESERVED_QTY,
                       r.REMAIN AVAILABLE_QTY,
                       nvl(p.QUALITY_STATUS, 'UNKNOWN') QUALITY_STATUS,
                       r.TIME_OF_LAST_UPDATE
                  from RRL_REMAINS r
                  join RRL_CELLS c on c.CELL = r.CELL
                  join RRL_WARES w on w.ID = c.WARE_ID
                  left join RRL_PALLETS p on p.UID_PALLET = r.UID_POLETA
                  left join RRL_ARTICULS a on upper(a.ACTICUL) = upper(p.ARTICUL)
                  left join RRL_RAW_BATCH rb on rb.RAW_BATCH_ID = p.PROD_BATCH_ID
                  {where_sql}
                 order by w.ID, r.CELL, p.EXPIRY_DATE nulls last, p.ARTICUL, r.UID_POLETA
              )
             where rownum <= :limit
            """,
            params,
        )


def _model_dict(model) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
