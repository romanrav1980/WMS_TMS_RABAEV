from typing import Any

from ..oracle_gateway import OracleGateway
from ..schemas import FinishedGoodsSkuSettingsUpdateRequest


class FinishedGoodsService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_skus(
        self,
        search: str | None = None,
        only_active: int | None = 1,
        only_with_stock: int | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if search:
            conditions.append("(upper(src.ARTICUL) like :search or upper(a.NAME) like :search)")
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
                select src.ARTICUL,
                       a.NAME,
                       a.UNIT_TYPE,
                       a.CELL DEFAULT_CELL,
                       a.BESTBEFOREDAYS SHELF_LIFE_DAYS,
                       a.SHIPMENT_AGING_HOURS,
                       a.SHIPMENT_AGING_COMMENT,
                       nvl(s.IS_FINISHED_GOODS, case when upper(a.ACTICUL) like 'FG-%' then 1 else 0 end) IS_FINISHED_GOODS,
                       s.PRODUCT_GROUP,
                       nvl(s.GTIN, b.GTIN) GTIN,
                       nvl(s.CRPT_REQUIRED, nvl(b.CRPT_REQUIRED, 0)) CRPT_REQUIRED,
                       nvl(s.AGGREGATION_REQUIRED, 0) AGGREGATION_REQUIRED,
                       nvl(s.SSCC_REQUIRED, 1) SSCC_REQUIRED,
                       nvl(s.PALLET_LABEL_REQUIRED, 1) PALLET_LABEL_REQUIRED,
                       nvl(s.QUALITY_HOLD_REQUIRED, 0) QUALITY_HOLD_REQUIRED,
                       s.DEFAULT_PALLET_CASE_QTY,
                       s.DEFAULT_LAYER_QTY,
                       s.DEFAULT_LAYER_COUNT,
                       s.TECHNOLOGIST_COMMENT,
                       nvl(s.ACTIVE, 1) ACTIVE,
                       nvl(st.TOTAL_REMAIN, 0) TOTAL_REMAIN,
                       nvl(st.PALLET_COUNT, 0) PALLET_COUNT,
                       nvl(pb.BATCH_COUNT, 0) BATCH_COUNT,
                       st.NEAREST_EXPIRY_DATE
                  from (
                    select upper(substr(ARTICUL, 1, 40)) ARTICUL
                      from RRL_FINISHED_GOODS_SKU
                     where ARTICUL is not null
                    union
                    select upper(substr(ACTICUL, 1, 40)) ARTICUL
                      from RRL_ARTICULS
                     where upper(ACTICUL) like 'FG-%'
                    union
                    select upper(substr(ARTICUL, 1, 40)) ARTICUL
                      from RRL_PROD_BATCH
                     where ARTICUL is not null
                    union
                    select upper(substr(p.ARTICUL, 1, 40)) ARTICUL
                      from RRL_PALLETS p
                      join RRL_REMAINS r on r.UID_POLETA = p.UID_PALLET
                      join RRL_CELLS c on c.CELL = r.CELL
                      join RRL_WARES w on w.ID = c.WARE_ID
                     where p.ARTICUL is not null
                       and (nvl(w.FLAG_FINISHED_GOODS, 0) = 1 or nvl(w.FLAG_PRODUCTION_BUFFER, 0) = 1)
                       and nvl(r.REMAIN, 0) <> 0
                  ) src
                  left join RRL_ARTICULS a
                    on upper(a.ACTICUL) = src.ARTICUL
                  left join RRL_FINISHED_GOODS_SKU s
                    on upper(s.ARTICUL) = src.ARTICUL
                  left join (
                    select upper(ARTICUL) ARTICUL,
                           max(GTIN) GTIN,
                           max(nvl(CRPT_REQUIRED, 0)) CRPT_REQUIRED
                      from RRL_PROD_BATCH
                     where ARTICUL is not null
                     group by upper(ARTICUL)
                  ) b on b.ARTICUL = src.ARTICUL
                  left join (
                    select upper(ARTICUL) ARTICUL,
                           count(*) BATCH_COUNT
                      from RRL_PROD_BATCH
                     where ARTICUL is not null
                     group by upper(ARTICUL)
                  ) pb on pb.ARTICUL = src.ARTICUL
                  left join (
                    select upper(p.ARTICUL) ARTICUL,
                           sum(nvl(r.REMAIN, 0)) TOTAL_REMAIN,
                           count(distinct r.UID_POLETA) PALLET_COUNT,
                           min(p.EXPIRY_DATE) NEAREST_EXPIRY_DATE
                      from RRL_PALLETS p
                      join RRL_REMAINS r on r.UID_POLETA = p.UID_PALLET
                      join RRL_CELLS c on c.CELL = r.CELL
                      join RRL_WARES w on w.ID = c.WARE_ID
                     where (nvl(w.FLAG_FINISHED_GOODS, 0) = 1 or nvl(w.FLAG_PRODUCTION_BUFFER, 0) = 1)
                       and nvl(r.REMAIN, 0) <> 0
                     group by upper(p.ARTICUL)
                  ) st on st.ARTICUL = src.ARTICUL
                  {where_sql}
                 order by src.ARTICUL
              )
             where rownum <= :limit
            """,
            params,
        )

    def update_sku_settings(self, articul: str, request: FinishedGoodsSkuSettingsUpdateRequest) -> int:
        params = {"articul": articul, **_model_dict(request)}
        return self.gateway.execute(
            """
            merge into RRL_FINISHED_GOODS_SKU d
            using (
              select upper(substr(:articul, 1, 40)) ARTICUL,
                     :is_finished_goods IS_FINISHED_GOODS,
                     :product_group PRODUCT_GROUP,
                     :gtin GTIN,
                     :crpt_required CRPT_REQUIRED,
                     :aggregation_required AGGREGATION_REQUIRED,
                     :sscc_required SSCC_REQUIRED,
                     :pallet_label_required PALLET_LABEL_REQUIRED,
                     :quality_hold_required QUALITY_HOLD_REQUIRED,
                     :default_pallet_case_qty DEFAULT_PALLET_CASE_QTY,
                     :default_layer_qty DEFAULT_LAYER_QTY,
                     :default_layer_count DEFAULT_LAYER_COUNT,
                     :technologist_comment TECHNOLOGIST_COMMENT,
                     :active ACTIVE,
                     :updated_by UPDATED_BY
                from dual
            ) s
            on (upper(d.ARTICUL) = s.ARTICUL)
            when matched then update set
              d.IS_FINISHED_GOODS = nvl(s.IS_FINISHED_GOODS, d.IS_FINISHED_GOODS),
              d.PRODUCT_GROUP = nvl(s.PRODUCT_GROUP, d.PRODUCT_GROUP),
              d.GTIN = nvl(s.GTIN, d.GTIN),
              d.CRPT_REQUIRED = nvl(s.CRPT_REQUIRED, d.CRPT_REQUIRED),
              d.AGGREGATION_REQUIRED = nvl(s.AGGREGATION_REQUIRED, d.AGGREGATION_REQUIRED),
              d.SSCC_REQUIRED = nvl(s.SSCC_REQUIRED, d.SSCC_REQUIRED),
              d.PALLET_LABEL_REQUIRED = nvl(s.PALLET_LABEL_REQUIRED, d.PALLET_LABEL_REQUIRED),
              d.QUALITY_HOLD_REQUIRED = nvl(s.QUALITY_HOLD_REQUIRED, d.QUALITY_HOLD_REQUIRED),
              d.DEFAULT_PALLET_CASE_QTY = nvl(s.DEFAULT_PALLET_CASE_QTY, d.DEFAULT_PALLET_CASE_QTY),
              d.DEFAULT_LAYER_QTY = nvl(s.DEFAULT_LAYER_QTY, d.DEFAULT_LAYER_QTY),
              d.DEFAULT_LAYER_COUNT = nvl(s.DEFAULT_LAYER_COUNT, d.DEFAULT_LAYER_COUNT),
              d.TECHNOLOGIST_COMMENT = nvl(s.TECHNOLOGIST_COMMENT, d.TECHNOLOGIST_COMMENT),
              d.ACTIVE = nvl(s.ACTIVE, d.ACTIVE),
              d.UPDATED_BY = nvl(s.UPDATED_BY, d.UPDATED_BY),
              d.UPDATED_AT = systimestamp
            when not matched then insert (
              ARTICUL, IS_FINISHED_GOODS, PRODUCT_GROUP, GTIN, CRPT_REQUIRED,
              AGGREGATION_REQUIRED, SSCC_REQUIRED, PALLET_LABEL_REQUIRED,
              QUALITY_HOLD_REQUIRED, DEFAULT_PALLET_CASE_QTY, DEFAULT_LAYER_QTY,
              DEFAULT_LAYER_COUNT, TECHNOLOGIST_COMMENT, ACTIVE, CREATED_BY,
              CREATED_AT, UPDATED_BY, UPDATED_AT
            ) values (
              s.ARTICUL, nvl(s.IS_FINISHED_GOODS, 1), s.PRODUCT_GROUP, s.GTIN, nvl(s.CRPT_REQUIRED, 0),
              nvl(s.AGGREGATION_REQUIRED, 0), nvl(s.SSCC_REQUIRED, 1), nvl(s.PALLET_LABEL_REQUIRED, 1),
              nvl(s.QUALITY_HOLD_REQUIRED, 0), s.DEFAULT_PALLET_CASE_QTY, s.DEFAULT_LAYER_QTY,
              s.DEFAULT_LAYER_COUNT, s.TECHNOLOGIST_COMMENT, nvl(s.ACTIVE, 1), nvl(s.UPDATED_BY, 'API'),
              systimestamp, nvl(s.UPDATED_BY, 'API'), systimestamp
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
                       case
                         when nvl(w.FLAG_FINISHED_GOODS, 0) = 1 then 'FINISHED_GOODS'
                         when nvl(w.FLAG_PRODUCTION_BUFFER, 0) = 1 then 'PRODUCTION_BUFFER'
                         else 'OTHER'
                       end WAREHOUSE_ROLE,
                       w.PREFIX,
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
                 where nvl(w.FLAG_FINISHED_GOODS, 0) = 1
                    or nvl(w.FLAG_PRODUCTION_BUFFER, 0) = 1
                 group by w.ID, w.NAME, w.FLAG_FINISHED_GOODS, w.FLAG_PRODUCTION_BUFFER,
                          w.PREFIX, w.DEFAULT_RECEIVE_CELL, w.DEFAULT_ISSUE_CELL, w.WARE_COMMENT
                 order by nvl(w.ID, 0)
              )
             where rownum <= :limit
            """,
            {"limit": min(max(limit, 1), 500)},
        )

    def list_batches(
        self,
        prod_batch_id: int | None = None,
        articul: str | None = None,
        batch_no: str | None = None,
        quality_status: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if prod_batch_id is not None:
            conditions.append("b.PROD_BATCH_ID = :prod_batch_id")
            params["prod_batch_id"] = int(prod_batch_id)
        if articul:
            conditions.append("upper(b.ARTICUL) like :articul")
            params["articul"] = f"%{articul.upper()}%"
        if batch_no:
            conditions.append("upper(b.PROD_BATCH_NO) like :batch_no")
            params["batch_no"] = f"%{batch_no.upper()}%"
        if quality_status:
            conditions.append("upper(nvl(b.QUALITY_STATUS, 'UNKNOWN')) = :quality_status")
            params["quality_status"] = quality_status.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select b.PROD_BATCH_ID,
                       b.PROD_BATCH_NO,
                       b.PRODUCTION_ORDER_ID,
                       b.ARTICUL,
                       b.GTIN,
                       b.PRODUCT_NAME,
                       b.PRODUCED_DATE_FROM,
                       b.PRODUCED_DATE_TO,
                       b.EXPIRY_DATE_FROM,
                       b.EXPIRY_DATE_TO,
                       b.TOTAL_QUANTITY,
                       b.TOTAL_PACK_COUNT,
                       b.UNIT_CODE,
                       b.WARE_ID,
                       w.NAME WARE_NAME,
                       nvl(b.QUALITY_STATUS, 'UNKNOWN') QUALITY_STATUS,
                       nvl(b.MERCURY_STATUS, 'NOT_REQUIRED') MERCURY_STATUS,
                       nvl(b.CRPT_STATUS, 'NOT_REQUIRED') CRPT_STATUS,
                       b.AGING_REQUIRED_HOURS,
                       b.SHIPMENT_ALLOWED_AT,
                       b.SHIPMENT_RELEASE_STATUS,
                       case
                         when b.SHIPMENT_ALLOWED_AT is null then 1
                         when b.SHIPMENT_ALLOWED_AT <= sysdate then 1
                         else 0
                       end IS_PLANNING_ALLOWED,
                       nvl(pc.PALLET_COUNT, 0) PALLET_COUNT,
                       nvl(cc.CODE_COUNT, 0) CRPT_CODE_COUNT,
                       nvl(ac.AGGREGATION_COUNT, 0) AGGREGATION_COUNT
                  from RRL_PROD_BATCH b
                  left join RRL_WARES w on w.ID = b.WARE_ID
                  left join (
                    select PROD_BATCH_ID, count(*) PALLET_COUNT
                      from RRL_PROD_BATCH_PALLETS
                     group by PROD_BATCH_ID
                  ) pc on pc.PROD_BATCH_ID = b.PROD_BATCH_ID
                  left join (
                    select PROD_BATCH_ID, count(*) CODE_COUNT
                      from RRL_CRPT_CODES
                     group by PROD_BATCH_ID
                  ) cc on cc.PROD_BATCH_ID = b.PROD_BATCH_ID
                  left join (
                    select PROD_BATCH_ID, count(*) AGGREGATION_COUNT
                      from RRL_CRPT_AGGREGATION
                     group by PROD_BATCH_ID
                  ) ac on ac.PROD_BATCH_ID = b.PROD_BATCH_ID
                  {where_sql}
                 order by b.PROD_BATCH_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_remains(
        self,
        prod_batch_id: int | None = None,
        articul: str | None = None,
        ware_id: int | None = None,
        ware_ids: str | None = None,
        prod_batch_no: str | None = None,
        cell: str | None = None,
        quality_status: str | None = None,
        only_available: int | None = 1,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        conditions = ["(nvl(w.FLAG_FINISHED_GOODS, 0) = 1 or nvl(w.FLAG_PRODUCTION_BUFFER, 0) = 1)"]
        params: dict[str, Any] = {"limit": min(max(limit, 1), 1000)}
        if prod_batch_id is not None:
            conditions.append("b.PROD_BATCH_ID = :prod_batch_id")
            params["prod_batch_id"] = int(prod_batch_id)
        if articul:
            conditions.append("upper(p.ARTICUL) like :articul")
            params["articul"] = f"%{articul.upper()}%"
        if ware_id is not None:
            conditions.append("w.ID = :ware_id")
            params["ware_id"] = int(ware_id)
        elif ware_ids:
            parsed = [int(value.strip()) for value in ware_ids.split(",") if value.strip().isdigit()][:100]
            if parsed:
                placeholders = []
                for idx, value in enumerate(parsed):
                    key = f"ware_id_{idx}"
                    placeholders.append(f":{key}")
                    params[key] = value
                conditions.append(f"w.ID in ({', '.join(placeholders)})")
        if prod_batch_no:
            conditions.append("upper(nvl(b.PROD_BATCH_NO, to_char(p.PROD_BATCH_ID))) like :prod_batch_no")
            params["prod_batch_no"] = f"%{prod_batch_no.upper()}%"
        if cell:
            conditions.append("upper(r.CELL) like :cell")
            params["cell"] = f"%{cell.upper()}%"
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
                       b.PROD_BATCH_ID,
                       b.PROD_BATCH_NO,
                       p.PRODUCED_DATE,
                       p.EXPIRY_DATE,
                       r.REMAIN QTY,
                       0 RESERVED_QTY,
                       r.REMAIN AVAILABLE_QTY,
                       nvl(p.QUALITY_STATUS, 'UNKNOWN') QUALITY_STATUS,
                       nvl(p.CRPT_STATUS, nvl(b.CRPT_STATUS, 'NOT_REQUIRED')) CRPT_STATUS,
                       nvl(ag.AGGREGATION_STATUS, 'NONE') AGGREGATION_STATUS,
                       b.SHIPMENT_ALLOWED_AT,
                       r.TIME_OF_LAST_UPDATE
                  from RRL_REMAINS r
                  join RRL_CELLS c on c.CELL = r.CELL
                  join RRL_WARES w on w.ID = c.WARE_ID
                  left join RRL_PALLETS p on p.UID_PALLET = r.UID_POLETA
                  left join RRL_ARTICULS a on upper(a.ACTICUL) = upper(p.ARTICUL)
                  left join RRL_PROD_BATCH b on b.PROD_BATCH_ID = p.PROD_BATCH_ID
                  left join RRL_CRPT_AGGREGATION ag on ag.UID_PALLET = p.UID_PALLET
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
