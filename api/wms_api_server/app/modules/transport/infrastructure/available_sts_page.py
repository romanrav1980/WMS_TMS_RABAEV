from typing import Any

def _window(sql: str) -> str:
    return ("select * from (select page_rows.*,rownum AS PAGE_ROW_NUMBER from ("+sql+
            ") page_rows where rownum<=:page_end) where PAGE_ROW_NUMBER>:page_offset order by PAGE_ROW_NUMBER")

def page_available_sts(sql: str, where_sql: str, has_having: bool, page: int | None,
                       size: int | None, params: dict[str,Any]) -> str:
    if page is None and size is None:
        return sql
    offset=((page or 1)-1)*(size or 100)
    params.update(page_end=offset+(size or 100),page_offset=offset)
    if has_having:
        return _window(sql)
    # RRL_ADDR.ADDR is unique; address attributes are functionally determined by ADDR.
    # Keep the header hash/sort narrow instead of grouping all long address strings.
    headers=("select P.ST_NUMBER,P.ADDR,P.WARE_ID from RABAEV.RRL_SBORKA_PALLETS P "
             "left join RABAEV.RRL_ADDR A on A.ADDR=P.ADDR "+where_sql+
             " and exists(select 1 from RABAEV.RRL_SBORKA_PALLET_ROWS R where R.PALLET_UID=P.PALLET_UID) "
             "group by P.ST_NUMBER,P.ADDR,P.WARE_ID")
    headers=("select H.ST_NUMBER,H.ADDR,H.WARE_ID from ("+headers+") H "
             "left join RABAEV.RRL_ADDR PAGE_ADDR on PAGE_ADDR.ADDR=H.ADDR "
             "order by PAGE_ADDR.ORD NULLS LAST,NVL(PAGE_ADDR.REGION,H.ADDR),H.ST_NUMBER,H.WARE_ID,H.ADDR")
    # Bounded header view drives existing ST_NUMBER and PALLET_UID indexes.
    source="FROM RABAEV.RRL_SBORKA_PALLETS P"
    join=("FROM ("+_window(headers)+") K JOIN RABAEV.RRL_SBORKA_PALLETS P ON "
          "(P.ST_NUMBER=K.ST_NUMBER OR (P.ST_NUMBER IS NULL AND K.ST_NUMBER IS NULL)) "
          "AND DECODE(P.ADDR,K.ADDR,1,0)=1 AND DECODE(P.WARE_ID,K.WARE_ID,1,0)=1")
    sql=sql.replace(source,join,1)
    return sql
