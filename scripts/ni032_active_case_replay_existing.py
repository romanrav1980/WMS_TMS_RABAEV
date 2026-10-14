"""148 direct-native history cannot be relabeled as another CASE API body."""
import sys,json
from pathlib import Path
import oracledb
from fastapi import HTTPException
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.services.case_pick_service import CasePickService
from app.schemas import CasePickLineConfirmRequest
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select OPERATION_ID,CANONICAL_REQUEST,RESULT_JSON from RRL_STOCK_OPERATION
 where COMMAND_TYPE='CASE_PICK_CONFIRM'and ACTOR='admin'and STATE='APPLIED'
 order by CREATED_AT desc fetch first 1 rows only""")
 op,wire,saved=q.fetchone()
 def read(value):
  if hasattr(value,"read"):value=value.read()
  return value if isinstance(value,dict)else json.loads(value)
 doc=read(wire);saved=read(saved);source=doc["source"]
 original=doc["metadata"].get("requested_confirmation")
 request=CasePickLineConfirmRequest(**(original or {**{k:v for k,v in doc["metadata"].items()if k in CasePickLineConfirmRequest.model_fields},"operation_id":op,"actor":doc["actor"]}))
 q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:op",op=op);before=q.fetchone()
 try:result=CasePickService().confirm_line(source["case_task_id"],source["case_line_id"],request)
 except HTTPException as exc:
  assert original is None and exc.status_code==409 and exc.detail["code"]=="OPERATION_CONTENT_CONFLICT",exc
 else:assert original is not None and result==saved,(result,saved)
 q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==before
 print("PASS148 existing native identity protected/conflict409/event unchanged; positive facade replay lacks original API fixture/op="+op if original is None else "PASS148 original API confirmation replay exact/event unchanged/op="+op,flush=True)
