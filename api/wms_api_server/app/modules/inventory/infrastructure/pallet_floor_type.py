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
                result=read_oracle_json(cur.callfunc("RRL_PALLET_FLOOR_READ.describe_type",oracledb.DB_TYPE_CLOB,[identifier,actor]))
                cur.execute("""select PALLET_TYPE_ID,PALLET_TYPE_CODE,PALLET_TYPE_NAME from RRL_PALLET_TYPE
                    where ACTIVE=1 order by PALLET_TYPE_ID fetch first 501 rows only""")
                rows=cur.fetchall()
                if len(rows)>500:
                    raise StockPostingError("PALLET_FLOOR_CATALOG_BOUND_500","READ",20886)
                result["types"]=[dict(zip(("id","code","name"),row))for row in rows]
                return result
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",None)
            if code is not None and 20800<=code<=20999:
                raise StockPostingError("PALLET_FLOOR_READ_REJECTED","READ",code,str(exc.args[0]).split("\n",1)[0])from exc
            raise

    def confirm(self,operation: str,identifier: str,metadata: dict[str,Any],actor: str)->dict[str,Any]:
        return self.posting.post(StockCommand(operation_id=operation,command_type="PALLET_FLOOR_TYPE_CONFIRM",
            actor=actor,source={"uid":identifier},lines=(),metadata=metadata))
