from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_case_labels.py");s=p.read_text(encoding="utf-8")+"""
from typing import Protocol
class CaseLabelPort(Protocol):
    def issue(self,task:int,request:CaseSsccLabelRequest,actor:str)->dict:...
    def current(self,task:int,actor:str)->dict:...
    def confirm(self,task:int,scan:str,actor:str)->dict:...
    def document(self,task:int,actor:str,format:str,dpi:int)->str:...
""";out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/case_label_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ....auth import","from ...platform.public import").replace("CaseSsccLabelRequest,CaseSsccConfirmRequest","CaseSsccLabelRequest,CaseSsccConfirmRequest,CaseLabelPort").replace("from ..infrastructure.case_labels import CaseLabels\n","").replace("from ....oracle_gateway import OracleGateway\n","").replace("def labels()->CaseLabels:return CaseLabels(OracleGateway())",'def labels()->CaseLabelPort:raise RuntimeError("CASE labels service not wired")').replace("service:CaseLabels","service:CaseLabelPort");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8").replace("from .api.case_label_routes import router as case_label_router","from .api.case_label_routes import router as case_label_router,labels as case_label_dependency")
s+="\nfrom .contracts_case_labels import CaseLabelPort\nfrom .infrastructure.case_labels import CaseLabels\ndef case_label_service()->CaseLabelPort:return CaseLabels(OracleGateway())\n";out[str(p)]=s
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8").replace("from .modules.inventory.public import case_label_router","from .modules.inventory.public import case_label_router,case_label_dependency,case_label_service");s+="\napp.dependency_overrides[case_label_dependency]=case_label_service\n";out[str(p)]=s
p=Path("scripts/ni042_case_sscc_case.py");s=p.read_text(encoding="utf-8")
needle='   label=call("POST",label_path,label_body);'
s=s.replace(needle,"""   try:q.callproc("RRL_CASE_SSCC_API.assert_ready",[case]);raise AssertionError("Unlabelled small CASE admitted")
   except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20887
"""+needle)
needle='   call("POST",label_path+"/confirm",{"scan":"(00)"+carrier})'
s=s.replace(needle,"""   try:q.callproc("RRL_CASE_SSCC_API.assert_ready",[case]);raise AssertionError("Unconfirmed label admitted")
   except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20887
"""+needle);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
