from .oracle_gateway import OracleGateway
from .modules.inventory.public import CaseTypePort,build_case_type,build_stock_posting_service

def build_case_type_service()->CaseTypePort:
    return build_case_type(OracleGateway(),build_stock_posting_service())
