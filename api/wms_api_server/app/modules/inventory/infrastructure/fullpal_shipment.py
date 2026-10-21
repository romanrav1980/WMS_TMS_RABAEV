from __future__ import annotations
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
"""Bind a physically confirmed whole pallet to an existing ST through the stock root."""
from ..contracts_stock import StockCommand, StockPostingError
from .stock_posting_uow import StockPosting


class FullPalletShipment:
    def __init__(self, gateway: OracleGateway | TransactionGateway) -> None:
        self.gateway = gateway

    def preview(self, task_id: int, actor: str | None = None) -> dict:
        rows = self.gateway.fetch_all("""
            select t.TASK_ID,pt.CUSTOMER_ORDER_ID,m.TARGET_UID_PALLET PALLET_IDENTIFIER,
                m.TO_CELL CELL,m.OPERATION_ID PHYSICAL_OPERATION_ID,s.STOCK_VERSION,
                RRL_STOCK_PLAN_HELPER.decimal_text(s.REMAIN) QUANTITY,s.BASE_UOM,p.ARTICUL ARTICLE,
                scope_cell.WARE_ID WAREHOUSE_ID,
                (select count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT ff where ff.PICKED_PALLET_UID=s.UID_POLETA and ff.STATUS in('PICKED','SHIPPED')) BOUND_SHIPMENTS,
                (select min(ff.PALLET_UID)from RRL_CUSTOMER_ORDER_FULFILLMENT ff where ff.PICKED_PALLET_UID=s.UID_POLETA and ff.STATUS in('PICKED','SHIPPED')) BOUND_SHIPMENT_IDENTIFIER
            from RRL_WAREHOUSE_TASK t
             join RRL_PICK_WAVE_TASK wt on wt.PICK_WAVE_TASK_ID=t.SOURCE_TASK_ID and wt.PICK_WAVE_ID=t.SOURCE_DOC_ID
             join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID and pt.TASK_TYPE='FULL_PALLET' and pt.STATUS='DONE'
             join RRL_WAREHOUSE_TASK_STOCK_MOVE m on m.TASK_ID=t.TASK_ID
             join RRL_STOCK_OPERATION op on op.OPERATION_ID=m.OPERATION_ID and op.STATE='APPLIED'
             join RRL_REMAINS s on s.UID_POLETA=m.TARGET_UID_PALLET and s.CELL=m.TO_CELL
             join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
             join RRL_CELLS scope_cell on scope_cell.CELL=s.CELL
            where t.TASK_ID=:task and t.STATUS='DONE' and t.TASK_SOURCE='WAVE' and t.TASK_TYPE='PICKING_MOVE'
              and RRL_ACCESS_API.allowed(:actor,'warehouse_task_view','WAREHOUSE',to_char(scope_cell.WARE_ID),t.ASSIGNED_TO)=1
              and not exists(select 1 from RRL_WMS_RECEIPT_UNIT u
                join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
                where u.CURRENT_UID=s.UID_POLETA
                  and RRL_TRADE_STOCK_GUARD.owner_allowed(:actor,scope_cell.WARE_ID,a.OWNER_ID,0)<>1)
            fetch first 2 rows only""", {"task": task_id, "actor": actor})
        if len(rows) != 1:
            raise ValueError("A confirmed full-pallet movement with one current physical lot is required")
        return rows[0]

    def bind(self, task_id: int, body: dict, actor: str) -> dict:
        return StockPosting().post(StockCommand(
            operation_id=body["operation_id"], command_type="PICK_PALLET_BIND_SHIPMENT", actor=actor,
            lines=(), source={"task_id": task_id},
            metadata={key: value for key, value in body.items() if key != "operation_id"},
        ))
