from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/integrations/domain/article_mapping.py");s=p.read_text(encoding="utf-8").replace("from .article_logistics import box_logistics","from .article_logistics import box_logistics\nfrom .article_units import map_units")
start=s.index('            elif segment == "E1BPE1MARMRT":')
end=s.index('        descriptions.sort',start)
s=s[:start]+s[end:]
s=s.replace('        descriptions.sort','        units = map_units(records)\n        descriptions.sort',1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/article_master.py");s=p.read_text(encoding="utf-8").replace("from ..domain.article_mapping import map_articles","from ..domain.article_mapping import map_articles\nfrom ..domain.article_units import merge_units")
s=s.replace("SOURCE_DOCNUM,BASE_UOM,SENDER from RRL_SAP_ARTICLE_META","SOURCE_DOCNUM,BASE_UOM,SENDER,UNITS_JSON from RRL_SAP_ARTICLE_META",1)
pos=s.index('        columns = {"NAME":')
s=s[:pos]+"""        unit = item["base_uom"] or (previous[2] if previous else None)
        if not unit:
            raise ValueError("Base UoM missing for new SAP mapping")
        merged = merge_units(read_oracle_json(previous[4]) if previous else [], item["units"], unit)
"""+s[pos:]
s=s.replace('"units": json.dumps(item["units"])','"units": json.dumps(merged)',1)
s=s.replace('*item["units"]]','*merged]',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
