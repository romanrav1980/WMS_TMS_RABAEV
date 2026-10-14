from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py");s=p.read_text(encoding="utf-8")
s=s.replace("select requested.ORIGINAL_LOAD,d.OPERATION_ID FINAL_LOAD","select /*+ leading(requested d f) use_nl(d f) index(d RRL_IW_DISPATCH_SOURCE_IX) */ requested.ORIGINAL_LOAD,d.OPERATION_ID FINAL_LOAD",1)
s=s.replace("select lineage.ORIGINAL_LOAD LOAD_OPERATION_ID","select /*+ leading(lineage receipt line transit loss confirmed issue) use_nl(receipt line transit loss confirmed issue) */ lineage.ORIGINAL_LOAD LOAD_OPERATION_ID",1)
print(json.dumps({p.as_posix():s}))
