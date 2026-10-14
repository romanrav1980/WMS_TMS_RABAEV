from pathlib import Path
import ast,json
root=Path("api/wms_api_server/app");out={}
p=root/"schemas.py";text=p.read_text(encoding="utf-8");tree=ast.parse(text);node=next(x for x in tree.body if isinstance(x,ast.ClassDef)and x.name=="OperationFactUpdate")
lines=text.splitlines(keepends=True);model="".join(lines[node.lineno-1:node.end_lineno]);del lines[node.lineno-1:node.end_lineno]
out[str(p)]="from .modules.transport.contracts import OperationFactUpdate\n"+"".join(lines)
p=root/"modules/transport/contracts.py";out[str(p)]=p.read_text(encoding="utf-8")+"\nfrom pydantic import BaseModel, Field\n\n"+model+"\n"
p=root/"modules/transport/api/operation_fact_routes.py";out[str(p)]=p.read_text(encoding="utf-8").replace("from ....schemas import OperationFactUpdate","from ..contracts import OperationFactUpdate")
print(json.dumps(out,ensure_ascii=True))
