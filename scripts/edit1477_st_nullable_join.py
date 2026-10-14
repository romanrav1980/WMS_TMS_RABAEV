from pathlib import Path
p=Path('api/wms_api_server/app/modules/transport/infrastructure/available_sts_page.py');before=p.read_text(encoding='utf-8');Path('tmp/available_sts_page_before1477.py').write_text(before,encoding='utf-8')
start=before.index('    # Bounded header view')
after='''    # Separate nullable ST keys so the normal branch can use an equality range scan.
    # The bounded key set is shared; NULL groups remain visible rather than discarded.
    keys = _window(headers)
    match = "DECODE(P.ADDR,K.ADDR,1,0)=1 AND DECODE(P.WARE_ID,K.WARE_ID,1,0)=1"
    selected = ("select P.* from ST_PAGE_KEYS K join RABAEV.RRL_SBORKA_PALLETS P "
                "on P.ST_NUMBER=K.ST_NUMBER and "+match+
                " union all select P.* from ST_PAGE_KEYS K join RABAEV.RRL_SBORKA_PALLETS P "
                "on P.ST_NUMBER is null and K.ST_NUMBER is null and "+match)
    sql = sql.replace("FROM RABAEV.RRL_SBORKA_PALLETS P", "FROM ("+selected+") P", 1)
    return "with ST_PAGE_KEYS as ("+keys+") "+sql
'''
p.write_text(before[:start]+after,encoding='utf-8')
