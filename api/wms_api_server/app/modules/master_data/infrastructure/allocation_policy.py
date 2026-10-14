"""Extend the existing warehouse/SKU rule; configuration owns one exclusive transaction."""
from typing import Any
from fastapi import HTTPException
from ...platform.public import stock_configuration_transaction

class AllocationPolicy:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def get(self,warehouse: int,article: str) -> dict[str,Any]:
        rows=self.gateway.fetch_all("""select STOCK_ALLOC_CLASS STOCK_CLASS,SHIP_FROM_STOCK,
            to_char(PICK_STEP_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PICK_STEP,
            ALLOCATION_VERSION POLICY_VERSION
            from RRL_RECEIPT_SKU_RULE where WARE_ID=:ware and ARTICUL=:article""",{"ware":warehouse,"article":article})
        value=rows[0] if rows else {"stock_class":"OTHER","ship_from_stock":None,"pick_step":"1","policy_version":0}
        override=value["ship_from_stock"]
        return {**value,"warehouse":warehouse,"article":article,
                "ship_from_stock":None if override is None else bool(override),
                "effective_ship_from_stock":bool(override) if override is not None else value["stock_class"]=="DRY_RACK"}

    def set(self,warehouse: int,article: str,request: Any,actor: str) -> dict[str,Any]:
        with stock_configuration_transaction(self.gateway,"Warehouse SKU allocation rule",actor,"warehouse_settings_edit") as cursor:
            cursor.execute("select count(*) from RRL_ARTICULS where ACTICUL=:article",{"article":article})
            if cursor.fetchone()[0]!=1:raise HTTPException(404,detail="SKU not found")
            cursor.execute("select RRL_STOCK_MATH.quantity(:p_step) from dual",{"p_step":request.pick_step})
            step=cursor.fetchone()[0]
            cursor.execute("select ALLOCATION_VERSION from RRL_RECEIPT_SKU_RULE where WARE_ID=:ware and ARTICUL=:article for update",{"ware":warehouse,"article":article})
            old=cursor.fetchone()
            if old is None:raise HTTPException(409,detail="Configure the warehouse SKU picking cell in receiving settings first")
            version=old[0]
            if version!=request.expected_version:raise HTTPException(409,detail="Allocation policy changed; reload")
            params={"ware":warehouse,"article":article,"kind":request.stock_class,
                    "flag":None if request.ship_from_stock is None else int(request.ship_from_stock),"step":step,"version":version+1}
            cursor.execute("""update RRL_RECEIPT_SKU_RULE set STOCK_ALLOC_CLASS=:kind,
                SHIP_FROM_STOCK=:flag,PICK_STEP_BASE=:step,ALLOCATION_VERSION=:version
                where WARE_ID=:ware and ARTICUL=:article""",params)
        return self.get(warehouse,article)
