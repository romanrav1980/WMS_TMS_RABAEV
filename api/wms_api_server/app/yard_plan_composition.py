"""Mount planned dock intervals of yard visits (TRADECASE T10, C-0158) on the native RRL_YARD_DOCK_PLAN_API."""
from fastapi import FastAPI
from .oracle_gateway import OracleGateway
from .modules.resources.public import OracleYardDockPlans, YardPlanPort, yard_plan_router, yard_plan_service


def build_yard_plans() -> YardPlanPort:
    return OracleYardDockPlans(OracleGateway())


def register_yard_plans(app: FastAPI) -> None:
    app.dependency_overrides[yard_plan_service] = build_yard_plans
    app.include_router(yard_plan_router)
