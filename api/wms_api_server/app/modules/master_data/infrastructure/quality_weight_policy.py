from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
from ..contracts_quality_weight import WeightPolicyInput
"""Explicit SI warehouse/SKU mass policy on the existing receipt SKU rule."""
from fastapi import HTTPException
from ...platform.public import stock_configuration_transaction


class QualityWeightPolicy:
    def __init__(self, gateway: OracleGateway | TransactionGateway) -> None:
        self.gateway = gateway

    def get(self, warehouse: int, article: str) -> dict:
        rows = self.gateway.fetch_all("""
            select QC_WEIGHT_VERSION VERSION,QC_WEIGHT_BASE_UOM BASE_UOM,
              RRL_STOCK_PLAN_HELPER.decimal_text(QC_BASE_WEIGHT_KG) BASE_WEIGHT_KG,
              RRL_STOCK_PLAN_HELPER.decimal_text(QC_BOX_WEIGHT_KG) BOX_WEIGHT_KG
            from RRL_RECEIPT_SKU_RULE where WARE_ID=:ware and ARTICUL=:article
            """, {"ware": warehouse, "article": article})
        if not rows:
            raise HTTPException(409, "Сначала настройте ячейку отбора товара в данном складе")
        return {"warehouse": warehouse, "article": article, **rows[0]}

    def set(self, warehouse: int, article: str, request: WeightPolicyInput, actor: str) -> dict:
        with stock_configuration_transaction(self.gateway, "SI outgoing QC mass policy", actor,
                                             "warehouse_settings_edit") as cursor:
            cursor.execute("select QC_WEIGHT_VERSION from RRL_RECEIPT_SKU_RULE where WARE_ID=:ware and ARTICUL=:article for update",
                           {"ware": warehouse, "article": article})
            old = cursor.fetchone()
            if old is None:
                raise HTTPException(409, "Сначала настройте ячейку отбора товара в данном складе")
            if old[0] != request.expected_version:
                raise HTTPException(409, "Настройка веса изменилась; загрузите её повторно")
            cursor.execute("select count(*) from RRL_STOCK_UOM_CONVERSION where ARTICUL=:article and INPUT_UOM=:base_uom and BASE_UOM=:base_uom and NUMERATOR=1 and DENOMINATOR=1", {"article":article,"base_uom":request.base_uom})
            if cursor.fetchone()[0]<1:
                raise HTTPException(409,"Базовая единица не подтверждена точным справочником единиц товара")
            cursor.execute("""update RRL_RECEIPT_SKU_RULE set QC_BASE_WEIGHT_KG=:base_weight,
                QC_BOX_WEIGHT_KG=:box_weight,QC_WEIGHT_BASE_UOM=:base_uom,QC_WEIGHT_VERSION=QC_WEIGHT_VERSION+1
                where WARE_ID=:ware and ARTICUL=:article""",
                {"ware": warehouse, "article": article, "base_weight": request.base_weight_kg,
                 "box_weight": request.box_weight_kg,"base_uom":request.base_uom})
        return self.get(warehouse, article)
