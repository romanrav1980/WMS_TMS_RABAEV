"""One metadata transaction owns original CASE identity and immutable label history."""
import json
import oracledb
from ....oracle_gateway import OracleGateway
from ...platform.public import read_oracle_json
from ..contracts_case_labels import CaseSsccLabelRequest
from ..contracts_stock import StockPostingError
from ..domain.pallet_identifiers import normalize_incoming_sscc
from ..domain.sscc_label import label_html,label_zpl
from .metadata_transactions import receipt_task_metadata

class CaseLabels:
    def __init__(self,gateway:OracleGateway)->None:
        self.gateway=gateway

    def _command(self,procedure:str,task:int,value:str,actor:str,operation:str="")->dict:
        try:
            with receipt_task_metadata(self.gateway,"Original CASE logistic label",actor,"case_pick_execute")as q:
                result=q.var(oracledb.DB_TYPE_CLOB)
                q.callproc(procedure,[task,value,actor,result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            error=exc.args[0];code=error.code
            raise StockPostingError("CASE_SSCC_REJECTED" if code and(code==1 or 20800<=code<=20899)else "RESULT_UNCERTAIN",operation,code,str(error.message).split("\n")[0])from exc

    def issue(self,task:int,request:CaseSsccLabelRequest,actor:str)->dict:
        wire=json.dumps(request.model_dump(),ensure_ascii=True,sort_keys=True,separators=(",",":"))
        return self._command("RRL_CASE_SSCC_API.issue",task,wire,actor,request.operation_id)

    def confirm(self,task:int,scan:str,actor:str)->dict:
        try:code=normalize_incoming_sscc(scan)
        except ValueError as exc:raise StockPostingError("CASE_SSCC_INVALID_SCAN","",20873,str(exc))from exc
        return self._command("RRL_CASE_SSCC_API.confirm_label",task,code,actor)

    def current(self,task:int,actor:str)->dict:
        try:
            with self.gateway.transaction("Current warehouse CASE logistic label read")as q:
                q.execute("set transaction read only")
                q.callproc("RRL_CASE_TASK_ACCESS.assert_scope",[task,actor,"case_pick_execute",None])
                q.execute("select l.RESULT_JSON,l.CONFIRMED_AT,l.CONFIRMED_BY,c.SSCC,c.CONTENT_VERSION,case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 1 else 0 end from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID left join RRL_CASE_SSCC_LABEL l on l.CASE_PICK_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:task",task=task)
                row=q.fetchone()
                if not row:raise StockPostingError("CASE_SSCC_SOURCE_REQUIRED","",20886)
                if row[0]is None:return {"case_pick_task_id":task,"issued":False,"final_scale_required":row[5]==1}
                result=read_oracle_json(row[0])
                return {**result,"issued":True,"confirmed":row[1]is not None,"confirmed_at":row[1].isoformat()if row[1]else None,"confirmed_by":row[2],"current_carrier":row[3],"current_content_version":int(row[4]),"final_scale_required":row[5]==1}
        except oracledb.DatabaseError as exc:
            error=exc.args[0]
            raise StockPostingError("CASE_SSCC_READ_REJECTED","",error.code,str(error.message).split("\n")[0])from exc

    def document(self,task:int,actor:str,format:str,dpi:int)->str:
        current=self.current(task,actor)
        if not current.get("issued"):raise StockPostingError("CASE_SSCC_NOT_ISSUED","",20873)
        data={"sscc":current["sscc"],"Задание":str(task)}
        return label_zpl(data,dpi,compact=True)if format=="zpl"else label_html(data,compact=True)
