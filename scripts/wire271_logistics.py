from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/integrations/domain/article_mapping.py");s=p.read_text(encoding="utf-8")
s=s.replace("from fractions import Fraction","from fractions import Fraction\nfrom .article_logistics import box_logistics",1)
s=s.replace('"units": units, "active":','"units": units, "logistics": box_logistics(records), "active":',1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/article_master.py");s=p.read_text(encoding="utf-8").replace('"COUNT_SHT_IN_KOR": item["box_qty"], "NORMA_UKLADKI": item["pallet_qty"]}','"COUNT_SHT_IN_KOR": item["box_qty"], "NORMA_UKLADKI": item["pallet_qty"], **item.get("logistics", {})}',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
