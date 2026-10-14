from .oracle_gateway import OracleGateway
from .modules.inventory.public import build_stock_posting_service
from .modules.fulfillment.public import PreparedLayoutPort, build_prepared_layout


def build_prepared_layout_service() -> PreparedLayoutPort:
    return build_prepared_layout(OracleGateway(), build_stock_posting_service())
