"""Typed physical carrier metadata through the same zero-quantity Root command."""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_stock import StockCommand,StockPostingError

class PalletFloorType:
    def __init__(self,gateway: Any,posting: Any)->None:
        self.gateway,self.posting=gateway,posting

    def read(self,identifier: str,actor: str)->dict[str,Any]:
        try:
            with self.gateway.transaction("Read current scoped full-pallet normative type")as cur:
                cur.execute("set transaction read only")
                return read_oracle_json(cur.callfunc("RRL_PALLET_FLOOR_READ.describe_type",oracledb.DB_TYPE_CLOB,[identifier,actor]))
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",None)
            if code is not None and 20800<=code<=20999:
                raise StockPostingError("PALLET_FLOOR_READ_REJECTED","READ",code,str(exc.args[0]).split("\n",1)[0])from exc
            raise

    def confirm(self,operation: str,identifier: str,metadata: dict[str,Any],actor: str)->dict[str,Any]:
        return self.posting.post(StockCommand(operation_id=operation,command_type="PALLET_FLOOR_TYPE_CONFIRM",
            actor=actor,source={"uid":identifier},lines=(),metadata=metadata))
