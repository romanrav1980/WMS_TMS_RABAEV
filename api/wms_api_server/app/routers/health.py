from fastapi import APIRouter

from ..oracle_gateway import OracleGateway
from ..schemas import DbPingResponse

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/db/ping", response_model=DbPingResponse)
def db_ping() -> dict[str, str]:
    return OracleGateway().ping()
