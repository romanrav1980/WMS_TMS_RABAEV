from typing import Any
import oracledb
from ..contracts_stock_settings import StockSettingError

class StockCompatibility:
    def __init__(self,gateway: Any) -> None:self.gateway=gateway
    def set_compatibility(self,enabled: bool,reason: str,actor: str) -> dict[str,Any]:
        try:
            with self.gateway.transaction("Maintain existing database-wide compatibility setting")as cur:
                cur.callproc("RRL_STOCK_SETTING_API.set_compatibility",["1"if enabled else"0",reason,actor])
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            raise StockSettingError(str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409 if 20800<=code<=20999 else 503) from exc
        return {"enabled":enabled,"scope":"DATABASE"}
