from pathlib import Path
import json
p=Path('api/wms_api_server/app/services/transport_service.py');s=p.read_text(encoding='utf-8')
a=s.index('    def list_available_sts(');b=s.index('    def _has_sborka_rows_for_period(',a);old=s[a:b]
# Preserve legacy predicates exactly; isolate the SQL builder in the owning module.
f=old[old.index('        conditions: list[str]'):old.index('        with _AVAILABLE_STS_CACHE_LOCK:',old.index('        where_sql'))]
x=f.index('        if (stdate is not None or date_to is not None)');y=f.index('        # Фильтр по складам',x);f=f[:x]+f[y:]
q=old[old.index('                SELECT P.ST_NUMBER,'):old.index('                """,',old.index('                SELECT P.ST_NUMBER,'))]
q=q.replace('P.ST_NUMBER\n','P.ST_NUMBER, P.WARE_ID, P.ADDR\n')
sig=old[:old.index('        cache_key =')].replace('    def list_available_sts(','def available_sts_query(').replace('        self,\n','').replace('    ) -> list[dict[str, Any]]:', '    ) -> tuple[str, dict[str, Any]]:')
f='\n'.join(line[4:]if line.startswith('    ')else line for line in f.splitlines())
f+='\n    sql = QUERY.format(where_sql=where_sql,having_sql=having_sql,weight_expr=weight_expr,volume_expr=volume_expr,verify_expr=verify_expr)\n    return sql, params\n'
helper='from datetime import date, timedelta\nfrom pathlib import Path\nfrom typing import Any\n\nQUERY = Path(__file__).with_suffix(".sql").read_text(encoding="utf-8")\n\n'+sig+f
# Delegate SQL and apply ROWNUM before fetch; cache remains shared with mutations.
names=['stdate','date_to','unassigned_only','ware_id','ware_ids','addr_mask','st_mask','st_mask_exclude','transport_type','assembled_only','not_assembled_only','max_weight_kg','max_volume_m3','articul','raion']
nsig=old[:old.index('        cache_key =')].replace('        raion: str | None = None,','        raion: str | None = None,\n        page: int | None = None,\n        page_size: int | None = None,')
body='        filters = dict(\n'+''.join('            '+n+'='+n+',\n'for n in names)+'        )\n'
body+='        cache_key = tuple(tuple(v) if isinstance(v,list) else v for v in filters.values())+(page,page_size)\n        with _AVAILABLE_STS_CACHE_LOCK:\n            cached = _AVAILABLE_STS_CACHE.get(cache_key)\n            if cached and time.monotonic()-cached[0] <= _AVAILABLE_STS_CACHE_TTL_SEC:\n                return [dict(row) for row in cached[1]]\n        sql, params = available_sts_query(**filters)\n        if page is not None or page_size is not None:\n            offset=((page or 1)-1)*(page_size or 100)\n            sql="select * from (select page_rows.*,rownum AS PAGE_ROW_NUMBER from ("+sql+") page_rows where rownum<=:page_end) where PAGE_ROW_NUMBER>:page_offset"\n            params.update(page_end=offset+(page_size or 100),page_offset=offset)\n        rows=self.gateway.fetch_all(sql,params)\n        for row in rows:\n            row.pop("PAGE_ROW_NUMBER",None)\n        normalized=[_fill_visible_time_window(dict(row)) for row in rows]\n        with _AVAILABLE_STS_CACHE_LOCK:\n            _AVAILABLE_STS_CACHE[cache_key]=(time.monotonic(),[dict(row) for row in normalized])\n        return normalized\n\n'
s=s[:a]+nsig+body+s[b:];s=s.replace('from ..modules.transport.public import normalize_transport_type as _normalize_transtype','from ..modules.transport.public import normalize_transport_type as _normalize_transtype, available_sts_query')
rp=Path('api/wms_api_server/app/routers/transport.py');r=rp.read_text(encoding='utf-8');a=r.index('def list_available_sts(');b=r.index('\n\n# ---',a);block=r[a:b];block=block.replace('        raion=raion,','        raion=raion,\n        page=page,\n        page_size=page_size,');x=block.index('    if page is not None');y=block.index('    return rows',x);y=block.index('\n    return rows',y)+1;block=block[:x]+block[y:];r=r[:a]+block+r[b:]
pub=Path('api/wms_api_server/app/modules/transport/public.py')
files={str(p):s,str(rp):r,str(pub):pub.read_text(encoding='utf-8')+'\nfrom .infrastructure.available_sts_query import available_sts_query\n','api/wms_api_server/app/modules/transport/infrastructure/available_sts_query.py':helper,'api/wms_api_server/app/modules/transport/infrastructure/available_sts_query.sql':q}
print(json.dumps(files,ensure_ascii=True))