from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_stock import StockCommand,StockPostingError

class CaseType:
    def __init__(self,gateway: Any,posting: Any)->None:
        self.gateway,self.posting=gateway,posting

    def read(self,task_id: int,actor: str)->dict[str,Any]:
        try:
            with self.gateway.transaction("Current recipient and actual CASE type READ ONLY")as cur:
                cur.execute("set transaction read only")
                return read_oracle_json(cur.callfunc("RRL_CASE_PALLET_TYPE_READ.describe_type",oracledb.DB_TYPE_CLOB,[task_id,actor]))
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",None)
            if code is not None and 20800<=code<=20999:
                raise StockPostingError("CASE_TYPE_READ_REJECTED","READ",code,str(exc.args[0]).split("\n",1)[0])from exc
            raise

    def change(self,task_id: int,operation: str,metadata: dict[str,Any],actor: str)->dict[str,Any]:
        return self.posting.post(StockCommand(operation_id=operation,command_type="CASE_PALLET_TYPE_CHANGE",
            actor=actor,source={"case_task_id":task_id},lines=(),metadata=metadata))
