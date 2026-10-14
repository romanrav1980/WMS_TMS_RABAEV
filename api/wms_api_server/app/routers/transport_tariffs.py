"""Read the existing carrier tariff catalog; never call mutating pricing functions."""
from fastapi import APIRouter, Depends, Query
from ..auth import AdminUser, TRANSPORT_DISPATCH_VIEW_PERMISSION, require_permission
from ..oracle_gateway import OracleGateway

router = APIRouter(prefix="/api/admin/transport/tariffs", tags=["transport-tariffs"])
_TABLE = "RRL_TRANSPORT_PRICE"


@router.get("")
def list_tariffs(
    region: str | None = Query(default=None, min_length=1, max_length=255),
    transport_type: str | None = Query(default=None, min_length=1, max_length=40),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Region is the original PRICE_NAME key; rates are exact decimal strings."""
    rows = OracleGateway().fetch_all("""
        select ID,PRICE_NAME,COMPANY,TYPE_TR,PRICE_FOLDER,
               to_char(PRICE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PRICE,
               to_char(PRICE_FOR_HOURS,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PRICE_FOR_HOURS,
               to_char(PRICE_FOR_ADDR,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PRICE_FOR_ADDR,
               to_char(NORM_HOURS,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') NORM_HOURS,
               to_char(RANGE1,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') RANGE1
          from RRL_TRANSPORT_PRICE
         where (:region_key is null or PRICE_NAME=:region_key)
           and (:vehicle_type is null or TYPE_TR=:vehicle_type
                or substr(PRICE_NAME,1,length(:vehicle_type)+2)='['||:vehicle_type||']')
         order by PRICE_NAME,COMPANY,ID fetch first 500 rows only
    """, {"region_key": region, "vehicle_type": transport_type})
    return [{str(k).upper(): v for k, v in row.items()} for row in rows]


@router.get("/table-info")
def get_tariff_table_info(
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    gw = OracleGateway()
    cols = gw.fetch_all("""
        select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS
         where TABLE_NAME=:table_name order by COLUMN_ID
    """, {"table_name": _TABLE})
    count = gw.fetch_all("select count(*) CNT from RRL_TRANSPORT_PRICE")
    return {
        "table": "RABAEV." + _TABLE,
        "columns": [{"name": str(c.get("column_name")), "type": str(c.get("data_type"))} for c in cols],
        "rows": int(count[0]["cnt"]),
        "rate_basis": {"PRICE": "VEHICLE", "PRICE_FOR_HOURS": "HOUR", "PRICE_FOR_ADDR": "POINT"},
        "region_basis": "ORIGINAL_PRICE_NAME_KEY",
        "norm_publication": "/api/finance/logistics-costs/transport-norms",
        "valuation_is_not_transport_fee": True,
    }
