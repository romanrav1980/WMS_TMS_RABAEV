from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/platform/public.py");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nfrom .infrastructure.oracle_json import read_oracle_json\n"
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py");s=p.read_text(encoding="utf-8-sig").replace("from ....oracle_gateway import OracleGateway","from ....oracle_gateway import OracleGateway\nfrom ...platform.public import read_oracle_json",1)
for expression in ["old_message[1]","known[0]","master[1]"]:s=s.replace("json.loads(self._text("+expression+"))","read_oracle_json("+expression+")")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/article_master.py");s=p.read_text(encoding="utf-8-sig").replace("from ....oracle_gateway import OracleGateway","from ....oracle_gateway import OracleGateway\nfrom ...platform.public import read_oracle_json",1)
for expression in ["row[2]","row[1]"]:s=s.replace("json.loads("+expression+".read() if hasattr("+expression+", \"read\") else "+expression+")","read_oracle_json("+expression+")")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receipt_commands.py");s=p.read_text(encoding="utf-8-sig").replace("from .placement import ReceiptPlacement","from .placement import ReceiptPlacement\nfrom ...platform.public import read_oracle_json",1).replace("json.loads(_text(cursor.fetchone()[0]))","read_oracle_json(cursor.fetchone()[0])",1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
