from pathlib import Path
import ast,json
root=Path("api/wms_api_server/app");out={}
def read(path):return out.get(str(path),path.read_text(encoding="utf-8"))
def save(path,text):ast.parse(text);out[str(path)]=text
gateway_import="from ....oracle_gateway import OracleGateway\nfrom ....transaction_gateway import TransactionGateway\n"
models={
 "case_short_commands":("CasePickShortDecisionRequest",{"request":"CasePickShortDecisionRequest"}),
 "mes_release_commands":("MesReleaseToProductionRequest",{"request":"MesReleaseToProductionRequest"}),
 "mes_supply_commands":("MesRawSupplyCalculateRequest",{"request":"MesRawSupplyCalculateRequest"}),
 "mes_task_commands":("MesRawTransferTaskConfirmRequest, MesRawTransferTaskCancelRequest",{"request":"MesRawTransferTaskConfirmRequest | MesRawTransferTaskCancelRequest"}),
 "reservation_commands":("StockReservationCreateRequest, StockReservationPromoteRequest, StockReservationStatusRequest",{"request":"StockReservationCreateRequest | StockReservationPromoteRequest | StockReservationStatusRequest"}),
 "terminal_quality_commands":("LotCheckRequest",{"request":"LotCheckRequest"}),
}
names=["case_shipment_binding","case_short_commands","document_reservation_commands","fullpal_shipment",
 "mes_release_commands","mes_supply_commands","mes_task_commands","reservation_commands","terminal_quality_commands","wave_commands","wave_execution","wave_pick_release"]
def annotate(text,mapping,returns):
 lines=text.splitlines(keepends=True);tree=ast.parse(text);changes=[]
 for fn in ast.walk(tree):
  if not isinstance(fn,ast.FunctionDef):continue
  args=fn.args.posonlyargs+fn.args.args+fn.args.kwonlyargs
  selected=[a for a in args if a.annotation is None and a.arg in mapping]
  if not selected and fn.returns is not None:continue
  signature="".join(lines[fn.lineno-1:fn.body[0].lineno-1])
  # Function signature starts before first body. Replace exact untyped argument name.
  import re
  for a in selected:
   signature=re.sub(r"(?<![\w.])"+a.arg+r"(?=\s*[,)=])",a.arg+": "+mapping[a.arg],signature,count=1)
  if fn.args.kwarg and fn.args.kwarg.annotation is None and fn.args.kwarg.arg in mapping:
   a=fn.args.kwarg;signature=signature.replace("**"+a.arg,"**"+a.arg+": "+mapping[a.arg])
  if fn.returns is None and fn.name in returns:
   pos=signature.rfind(":")
   signature=signature[:pos]+" -> "+returns[fn.name]+signature[pos:]
  changes.append((fn.lineno-1,fn.body[0].lineno-1,signature))
 for start,end,value in sorted(changes,reverse=True):lines[start:end]=[value]
 return "".join(lines)
for name in names:
 p=root/f"modules/inventory/infrastructure/{name}.py";text=read(p)
 text="from __future__ import annotations\n"+gateway_import+text
 mapping={"gateway":"OracleGateway | TransactionGateway"}
 if name in models:
  imports,extra=models[name];text="from ....schemas import "+imports+"\n"+text if False else text.replace(gateway_import,gateway_import+"from ....schemas import "+imports+"\n",1)
  mapping.update(extra)
 text=annotate(text,mapping,{"__init__":"None","post_short_approval":"dict[str, Any]","release_supply":"dict[str, Any]","calculate_supply":"dict[str, Any]","post_mes_task":"dict[str, Any]","post_reservation":"dict[str, Any]","post_terminal_quality":"dict[str, Any]"})
 if "Any"in text and "from typing import Any"not in text:text=text.replace(gateway_import,gateway_import+"from typing import Any\n",1)
 save(p,text)
p=root/"modules/inventory/infrastructure/metadata_transactions.py";text=read(p)
text="from collections.abc import Iterator\nimport oracledb\n"+gateway_import+text
text=annotate(text,{"gateway":"OracleGateway | TransactionGateway"},{"receipt_task_metadata":"Iterator[oracledb.Cursor]"});save(p,text)
p=root/"modules/inventory/infrastructure/placement.py";text=read(p)
text=text.replace("def _limit(value, maximum, title: str)","def _limit(value: Decimal | str | float | int | None, maximum: Decimal | float | int | None, title: str)")
save(p,text)
# Task port is a contract, not an infrastructure-private type.
p=root/"modules/inventory/infrastructure/task_completion.py";text=read(p)
start=text.index("class TaskActionHandler(Protocol):");end=text.index("\n\ndef run_existing_task_action(",start)
protocol=text[start:end]
contract="from typing import Any, Protocol\nfrom ...schemas import WarehouseTaskStatusRequest\n\n"+protocol+"\n"
save(root/"modules/inventory/contracts_task_actions.py",contract)
text=text[:start]+text[end:];text=text.replace("from typing import Any, Protocol","from typing import Any").replace("from ..contracts_stock import StockCommand, StockPostingError","from ..contracts_stock import StockCommand, StockPostingError\nfrom ..contracts_task_actions import TaskActionHandler")
save(p,text)
# Existing API DTO moved to owner contract and old router alias preserved.
p=root/"routers/case_pick.py";text=read(p);tree=ast.parse(text)
node=next(x for x in tree.body if isinstance(x,ast.ClassDef)and x.name=="CaseCarrierReturnRequest")
lines=text.splitlines(keepends=True);model="".join(lines[node.lineno-1:node.end_lineno])
save(root/"modules/inventory/contracts_case_return.py","from pydantic import BaseModel, Field\n\n"+model+"\n")
del lines[node.lineno-1:node.end_lineno];text="".join(lines)
text="from ..modules.inventory.public import CaseCarrierReturnRequest\n"+text
text=text.replace("from ..modules.inventory.contracts_stock import StockPostingError","from ..modules.inventory.public import StockPostingError")
save(p,text)
# Weight input contract avoids infrastructure importing an API.
p=root/"modules/master_data/api/quality_weight_routes.py";text=read(p);tree=ast.parse(text)
node=next(x for x in tree.body if isinstance(x,ast.ClassDef)and x.name=="WeightPolicyInput")
lines=text.splitlines(keepends=True);model="".join(lines[node.lineno-1:node.end_lineno])
save(root/"modules/master_data/contracts_quality_weight.py","from decimal import Decimal\nfrom pydantic import BaseModel, ConfigDict, Field\n\n"+model+"\n")
del lines[node.lineno-1:node.end_lineno];text="".join(lines)
text="from ..contracts_quality_weight import WeightPolicyInput\n"+text
text=text.replace("article: str, request, actor: str","article: str, request: WeightPolicyInput, actor: str")
save(p,text)
p=root/"modules/master_data/infrastructure/quality_weight_policy.py";text=read(p)
text=gateway_import+"from ..contracts_quality_weight import WeightPolicyInput\n"+text
text=annotate(text,{"gateway":"OracleGateway | TransactionGateway","request":"WeightPolicyInput"},{"__init__":"None"})
save(p,text)
p=root/"modules/master_data/infrastructure/receipt_policy.py";save(p,read(p).replace("from ...inventory.infrastructure.configuration_uow import configuration_transaction","from ...platform.public import stock_configuration_transaction as configuration_transaction"))
# Public parameters use concrete DTOs and an explicit transaction-bound factory.
p=root/"modules/inventory/public.py";text=read(p)
header="""from __future__ import annotations
from typing import Any
from contextlib import AbstractContextManager
import oracledb
from ...transaction_gateway import TransactionGateway
from ...schemas import (WarehouseTaskStatusRequest, MesRawTransferTaskConfirmRequest, MesRawTransferTaskCancelRequest,
    MesRawSupplyCalculateRequest, CasePickLineConfirmRequest, CasePickShortDecisionRequest, LotCheckRequest)
from .contracts_task_actions import TaskActionHandler
from .contracts_case_return import CaseCarrierReturnRequest
from .application.case_carrier_move import CaseCarrierMove
"""
text=header+text
mapping={"gateway":"OracleGateway | TransactionGateway","request":"Any","scope":"bool | str | None"}
returns={"inventory_configuration_transaction":"AbstractContextManager[oracledb.Cursor]",
 "warehouse_metadata_transaction":"AbstractContextManager[oracledb.Cursor]","post_existing_mes_task":"dict[str, Any]",
 "calculate_existing_mes_supply":"dict[str, Any]","post_existing_case_pick":"dict[str, Any]","existing_case_pick_policy":"dict[str, Any]",
 "build_case_carrier_move_service":"CaseCarrierMove","post_existing_case_short_approval":"dict[str, Any]",
 "post_existing_terminal_quality":"dict[str, Any]","bind_existing_case_shipment":"dict[str, Any]","return_existing_case_carrier":"dict[str, Any]"}
text=annotate(text,mapping,returns)
specific={"complete_existing_warehouse_task":"WarehouseTaskStatusRequest","run_existing_warehouse_task_action":"WarehouseTaskStatusRequest",
 "post_existing_mes_task":"MesRawTransferTaskConfirmRequest | MesRawTransferTaskCancelRequest","calculate_existing_mes_supply":"MesRawSupplyCalculateRequest",
 "post_existing_case_pick":"CasePickLineConfirmRequest","post_existing_case_short_approval":"CasePickShortDecisionRequest",
 "post_existing_terminal_quality":"LotCheckRequest","return_existing_case_carrier":"CaseCarrierReturnRequest"}
tree=ast.parse(text);lines=text.splitlines(keepends=True)
for fn in sorted((x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name in specific),key=lambda x:x.lineno,reverse=True):
 signature="".join(lines[fn.lineno-1:fn.body[0].lineno-1]).replace("request: Any","request: "+specific[fn.name])
 if fn.name=="complete_existing_warehouse_task":signature=signature.replace("-> None:","-> dict[str, Any]:")
 if fn.name=="run_existing_warehouse_task_action":signature=signature.replace("service_factory: Callable","service_factory: Callable[[TransactionGateway], TaskActionHandler]")
 lines[fn.lineno-1:fn.body[0].lineno-1]=[signature]
save(p,"".join(lines))
# Native adapter always handles terminal quality; no unreachable legacy DML tail.
p=root/"services/tserver_service.py";text=read(p);tree=ast.parse(text);cls=next(x for x in tree.body if isinstance(x,ast.ClassDef))
fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef)and x.name=="confirm_lot_check")
node=next(x for x in fn.body if isinstance(x,ast.If)and "post_existing_terminal_quality"in ast.unparse(x.test))
lines=text.splitlines(keepends=True);prefix="".join(lines[fn.lineno-1:node.lineno-1])
lines[fn.lineno-1:fn.end_lineno]=[prefix+"        post_existing_terminal_quality(self.gateway, usscc, request)\n"]
save(p,"".join(lines))
print(json.dumps(out,ensure_ascii=True))
