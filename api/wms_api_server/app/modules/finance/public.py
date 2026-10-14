from typing import Any
from .contracts import LogisticsCostPort,LogisticsCostError,logistics_cost_service
from .api.logistics_cost_routes import router as logistics_cost_router
from .infrastructure.logistics_costs import LogisticsCosts

def build_logistics_costs(gateway: Any) -> LogisticsCostPort:
    return LogisticsCosts(gateway)

from .contracts_expenses import LogisticsExpensePort,logistics_expense_service
from .api.logistics_expense_routes import router as logistics_expense_router
from .infrastructure.logistics_expenses import LogisticsExpenses

def build_logistics_expenses(gateway: Any) -> LogisticsExpensePort:
    return LogisticsExpenses(gateway)

from .contracts_allocation import ExpenseAllocationPort,expense_allocation_service
from .api.expense_allocation_routes import router as expense_allocation_router
from .infrastructure.expense_allocation import ExpenseAllocation

def build_expense_allocation(gateway: Any) -> ExpenseAllocationPort:
    return ExpenseAllocation(gateway)

from .contracts_reconciliation import DayReconciliationPort,day_reconciliation_service
from .api.day_reconciliation_routes import router as day_reconciliation_router
from .infrastructure.day_reconciliation import DayReconciliation

def build_day_reconciliation(gateway: Any) -> DayReconciliationPort:
    return DayReconciliation(gateway)

from .api.day_review_routes import router as day_review_router
from .contracts_day_reviews import day_reviews_service,DayReviewsPort
from .infrastructure.day_reviews import DayReviews

def build_day_reviews(gateway: Any) -> DayReviewsPort:
    return DayReviews(gateway)
