from .oracle_gateway import OracleGateway
from .modules.finance.public import DayReconciliationPort,build_day_reconciliation

def build_day_reconciliation_service() -> DayReconciliationPort:
    return build_day_reconciliation(OracleGateway())

from .modules.finance.public import build_day_reviews,DayReviewsPort

def build_day_reviews_service() -> DayReviewsPort:
    return build_day_reviews(OracleGateway())
