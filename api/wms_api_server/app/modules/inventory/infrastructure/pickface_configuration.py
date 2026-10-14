"""Master slot configuration preserves occupied old faces and current warehouse rights."""
from typing import Any
from fastapi import HTTPException
import oracledb
from ....schemas import PickFaceArticulUpsertRequest
from ....transaction_gateway import TransactionGateway
from ...platform.public import stock_configuration_transaction
from .pickface_attributes import _base_assign,_extended_attributes

def _identity(cur: Any,request: PickFaceArticulUpsertRequest,actor: str) -> tuple[int,str]:
    cur.execute("select WARE_ID,CELL_CODE from RRL_PICK_FACE where PICK_FACE_ID=:face for update",face=request.pick_face_id)
    face=cur.fetchone()
    if not face:raise HTTPException(404,detail="PICK_FACE_NOT_FOUND")
    warehouse,cell=face
    cur.execute("""select count(*)from RUSERS u where ID=:actor and nvl(DELETED,0)=0
        and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(ID,'pick_topology_edit')=1""",actor=actor,ware=warehouse)
    if cur.fetchone()[0]!=1:raise HTTPException(403,detail="PICK_FACE_CURRENT_WARE_ACTOR_REQUIRED")
    article=request.articul.strip().upper()
    if not article or len(article)>40:raise HTTPException(422,detail="PICK_FACE_ARTICLE_ID_BOUND_40")
    cur.execute("select count(*)from RRL_ARTICULS where ACTICUL=:article",article=article)
    if cur.fetchone()[0]!=1:raise HTTPException(409,detail="PICK_FACE_CURRENT_ARTICLE_REQUIRED")
    if request.pick_face_articul_id is not None:
        cur.execute("select PICK_FACE_ID,ARTICUL from RRL_PICK_FACE_ARTICUL where PICK_FACE_ARTICUL_ID=:id for update",id=request.pick_face_articul_id)
        previous=cur.fetchone()
        if not previous or previous!=(request.pick_face_id,article):raise HTTPException(409,detail="PICK_FACE_ROW_IDENTITY_CONFLICT")
    else:
        cur.execute("select PICK_FACE_ARTICUL_ID from RRL_PICK_FACE_ARTICUL where PICK_FACE_ID=:face and upper(ARTICUL)=:article",face=request.pick_face_id,article=article)
        rows=cur.fetchall()
        if len(rows)>1:raise HTTPException(409,detail="PICK_FACE_MAPPING_AMBIGUOUS")
    return int(warehouse),cell

def _preserve_occupied(cur: Any,cell: str,request: PickFaceArticulUpsertRequest) -> None:
    cur.execute("select trunc(sysdate)from dual");today=cur.fetchone()[0].date()
    withdraw=request.active==0 or request.case_pick_enabled==0 or (request.valid_from is not None and request.valid_from>today) or (request.valid_to is not None and request.valid_to<today)
    if not withdraw:return
    cur.execute("""select count(*)from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
        where r.CELL=:cell and p.ARTICUL=:article and(r.REMAIN>0 or r.HARD_RESERVED_BASE>0)""",cell=cell,article=request.articul.upper())
    if cur.fetchone()[0]:raise HTTPException(409,detail="PICK_FACE_OLD_STOCK_REQUIRES_DRAIN")
    cur.execute("""select count(*)from RRL_WAREHOUSE_TASK where TO_CELL=:cell
        and STATUS not in('DONE','CANCELLED')and(TARGET_ARTICUL=:article or RAW_ARTICUL=:article)""",cell=cell,article=request.articul.upper())
    if cur.fetchone()[0]:raise HTTPException(409,detail="PICK_FACE_OLD_TASK_REQUIRES_DRAIN")
    cur.execute("""select count(*)from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
        where l.CELL_CODE=:cell and l.ARTICUL=:article and l.STATUS not in('DONE','CANCELLED')and t.STATUS not in('DONE','CANCELLED')""",cell=cell,article=request.articul.upper())
    if cur.fetchone()[0]:raise HTTPException(409,detail="PICK_FACE_OLD_TASK_REQUIRES_DRAIN")

def configure_existing_pick_face_article(gateway: Any,request: PickFaceArticulUpsertRequest,actor: str) -> int:
    normalized=request.model_copy(update={"articul":request.articul.strip().upper(),"updated_by":actor})
    try:
        with stock_configuration_transaction(gateway,"Atomic original pick-face article settings",actor,"pick_topology_edit") as cur:
            _warehouse,cell=_identity(cur,normalized,actor)
            _preserve_occupied(cur,cell,normalized)
            bound=TransactionGateway(cur)
            identity=_base_assign(bound,normalized)
            _extended_attributes(bound,identity,normalized)
            return identity
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if code==1403:raise HTTPException(404,detail="PICK_FACE_CONFIGURATION_SOURCE_NOT_FOUND") from exc
        if code==20882:raise HTTPException(403,detail="PICK_FACE_CONFIGURATION_FORBIDDEN") from exc
        if 20800<=code<=20999 or code in {1,2290,2291,2292}:raise HTTPException(409,detail=str(exc.args[0]).split("\n",1)[0]) from exc
        if code in {6502,12899}:raise HTTPException(422,detail="PICK_FACE_CONFIGURATION_INPUT_INVALID") from exc
        raise HTTPException(503,detail="PICK_FACE_CONFIGURATION_UNCONFIRMED_REPEAT_ORIGINAL") from exc
