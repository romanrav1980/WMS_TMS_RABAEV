"""Use the original global pallet types behind the existing metadata transaction."""
import json
import oracledb
from ....oracle_gateway import OracleGateway
from ..contracts_pallet_types import PalletTypeUpsertRequest
from ..contracts_stock import StockPostingError
from .metadata_transactions import receipt_task_metadata


def upsert_pallet_type(gateway: OracleGateway,request: PalletTypeUpsertRequest)->int:
    actor=request.updated_by
    if not actor:
        raise StockPostingError("PALLET_TYPE_ACTOR_REQUIRED",None,20882)
    wire=json.dumps(request.model_dump(mode="json",exclude={"updated_by"}),ensure_ascii=True,sort_keys=True,separators=(",",":"))
    try:
        with receipt_task_metadata(gateway,"Existing carrier type and final weight policy",actor,"case_pick_manage")as q:
            result=q.var(oracledb.DB_TYPE_NUMBER)
            q.callproc("RRL_PALLET_TYPE_API.upsert_request",[wire,actor,result])
            return int(result.getvalue())
    except oracledb.DatabaseError as exc:
        code=exc.args[0].code
        raise StockPostingError("PALLET_TYPE_UPDATE_REJECTED" if code and(code==1 or 20800<=code<=20899)else "RESULT_UNCERTAIN",None,code)from exc
