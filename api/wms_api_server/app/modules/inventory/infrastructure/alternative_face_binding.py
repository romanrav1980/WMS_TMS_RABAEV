"""Apply one approved empty dynamic face to existing wave/CASE metadata."""
from typing import Any

def bind_alternative_face(cursor: Any,wave_id: int,row_id: int,article: str,old_cell: str,face: int,cell: str,
                          route_cell: int|None,route_sequence: int|None,sequence: int|None,unit_volume: Any,
                          base: str,actor: str,ids: str,source_reservation: int|None) -> None:
    cursor.execute("""insert into RRL_PICK_FACE_ASSIGNMENT(PICK_FACE_ASSIGNMENT_ID,PICK_FACE_ID,CELL_CODE,
        PICK_WAVE_ID,PICK_WAVE_REPLENISH_TASK_ID,ARTICUL,ASSIGNMENT_KIND,STATUS,ASSIGNED_AT,ASSIGNED_BY,
        UNIT_VOLUME_M3,BASE_UOM) values(RRL_PICK_FACE_ASSIGN_SQ.nextval,:face,:cell,:wave,:repl,:article,
        'DYNAMIC','ACTIVE',sysdate,:actor,:volume,:base)""",
        {"face": face, "cell": cell, "wave": wave_id, "repl": row_id, "article": article,
         "actor": actor, "volume": unit_volume, "base": base})
    values = {"wave": wave_id, "article": article, "old_cell": old_cell, "cell": cell,
              "face": face, "route_cell": route_cell, "sequence": route_sequence or sequence, "actor": actor}
    cursor.execute(f"""declare d RRL_PICK_WAVE_DEMAND%rowtype;
      begin
        select * into d from RRL_PICK_WAVE_DEMAND where PICK_WAVE_ID=:wave
          and ARTICUL=:article and TASK_TYPE='CASE_PICK' and TARGET_CELL_CODE=:old_cell;
        d.PICK_WAVE_DEMAND_ID:=RRL_PICK_WAVE_DEMAND_SQ.nextval;
        d.TARGET_CELL_CODE:=:cell;d.PICK_FACE_ID:=:face;d.PICK_ROUTE_CELL_ID:=:route_cell;
        select nvl(sum(QTY),0),count(*) into d.DEMAND_QTY,d.TASK_COUNT from RRL_PICK_WAVE_TASK
          where PICK_WAVE_ID=:wave and PICK_TASK_ID in ({ids});
        d.PICK_FACE_FREE_QTY:=0;d.REPLENISH_QTY:=d.DEMAND_QTY;
        insert into RRL_PICK_WAVE_DEMAND values d;
        update RRL_PICK_WAVE_DEMAND set DEMAND_QTY=greatest(DEMAND_QTY-d.DEMAND_QTY,0),
          TASK_COUNT=greatest(TASK_COUNT-d.TASK_COUNT,0)
          where PICK_WAVE_ID=:wave and ARTICUL=:article and TASK_TYPE='CASE_PICK' and TARGET_CELL_CODE=:old_cell;
      exception when no_data_found then null;end;""",
        {k:values[k] for k in ("cell","face","route_cell","wave","article","old_cell")})
    cursor.execute(f"""update RRL_PICK_WAVE_TASK set SOURCE_CELL_CODE=:cell,TARGET_CELL_CODE=:cell,
        PICK_FACE_ID=:face,PICK_ROUTE_CELL_ID=:route_cell,PICK_SEQUENCE=:sequence
        where PICK_WAVE_ID=:wave and ARTICUL=:article and TASK_TYPE='CASE_PICK'
          and nvl(TARGET_CELL_CODE,SOURCE_CELL_CODE)=:old_cell and PICK_TASK_ID in ({ids})""",
        {k: values[k] for k in ("cell","face","route_cell","sequence","wave","article","old_cell")})
    cursor.execute(f"""update RRL_PICK_TASK set SOURCE_CELL_CODE=:cell,TARGET_CELL_CODE=:cell,
        PICK_FACE_ID=:face,PICK_ROUTE_CELL_ID=:route_cell,PICK_SEQUENCE=:sequence
        where PICK_TASK_ID in(select PICK_TASK_ID from RRL_PICK_WAVE_TASK
          where PICK_WAVE_ID=:wave and ARTICUL=:article and TASK_TYPE='CASE_PICK' and SOURCE_CELL_CODE=:cell and PICK_TASK_ID in ({ids}))""",
        {k: values[k] for k in ("cell","face","route_cell","sequence","wave","article")})
    cursor.execute(f"""update RRL_CASE_PICK_LINE set CELL_CODE=:cell,PICK_FACE_ID=:face,
        PICK_ROUTE_CELL_ID=:route_cell,PICK_SEQUENCE=:sequence,UPDATED_AT=systimestamp,UPDATED_BY=:actor
        where PICK_WAVE_ID=:wave and ARTICUL=:article and CELL_CODE=:old_cell and nvl(PICKED_QTY,0)=0 and PICK_TASK_ID in ({ids})""", values)
    cursor.execute("""update RRL_CASE_PICK_TASK set CONTENT_VERSION=CONTENT_VERSION+1,UPDATED_AT=systimestamp,UPDATED_BY=:actor
        where CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from RRL_CASE_PICK_LINE
          where PICK_WAVE_ID=:wave and ARTICUL=:article and CELL_CODE=:cell)""",
        {k: values[k] for k in ("actor","wave","article","cell")})
    cursor.execute("""insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,
        OFFLINE_EVENT_ID,PAYLOAD_JSON,CREATED_BY)
        select RRL_CASE_PICK_EVENT_SQ.nextval,ct.CASE_PICK_TASK_ID,'FACE_TARGET_REROUTED',
          'ALT.FACE:'||to_char(:repl)||':'||to_char(ct.CASE_PICK_TASK_ID),
          json_object('replenishment_id' value :repl,'old_cell' value :old_cell,'new_cell' value :cell,
            'article' value :article,'content_version' value ct.CONTENT_VERSION returning clob),:actor
        from RRL_CASE_PICK_TASK ct where ct.PICK_WAVE_ID=:wave and exists(select 1 from RRL_CASE_PICK_LINE l
          where l.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID and l.ARTICUL=:article and l.CELL_CODE=:cell)""",
        {"repl":row_id,"old_cell":old_cell,"cell":cell,"article":article,"actor":actor,"wave":wave_id})
    cursor.execute(f"""update RRL_PICK_WAVE_REPLENISH_TASK set TARGET_CELL_CODE=:cell,STATUS='RELEASED',
        WAIT_REASON=null,RELEASED_AT=sysdate,RELEASED_BY=:actor,UPDATED_AT=sysdate,UPDATED_BY=:actor
        where PICK_WAVE_ID=:wave and ARTICUL=:article and TARGET_CELL_CODE=:old_cell
          and STATUS in('RELEASED','QUEUED','WAIT_FREE_CELL','FAILED')
          and (PICK_TASK_ID in ({ids}) or PICK_WAVE_REPLENISH_TASK_ID=:repl)""",
        {**{k: values[k] for k in ("cell","actor","wave","article","old_cell")},"repl":row_id})
    if source_reservation is not None:
        cursor.execute(f"""update RRL_PICK_WAVE_REPLENISH_TASK set TARGET_CELL_CODE=:cell,STATUS='RELEASED',
            WAIT_REASON=null,UPDATED_AT=sysdate,UPDATED_BY=:actor where PICK_WAVE_REPLENISH_TASK_ID=:repl""",
            {"cell":cell,"actor":actor,"repl":row_id})
