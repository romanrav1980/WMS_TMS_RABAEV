"""Existing shortage incident and CASE journal; reviews never conduct quantities."""
import json
from datetime import datetime, timezone
from typing import Any
from fastapi import HTTPException
from ...platform.public import stock_configuration_transaction
from ..domain.cctv_archive import archive_uri, validate_template, validate_uri

def payload(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else json.loads(value)

class ShortInvestigation:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def read(self, short_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all("""select sh.CASE_PICK_SHORT_ID SHORT_ID,sh.CASE_PICK_TASK_ID,
            sh.CASE_PICK_LINE_ID,sh.CELL_CODE CELL,ct.WARE_ID WAREHOUSE,sh.ARTICUL ARTICLE,
            sh.CREATED_AT,to_char(sh.CREATED_AT_INSTANT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') CREATED_INSTANT,sh.CREATED_BY,sh.REASON_TEXT,sh.STATUS,sh.RECOVERY_STATE,
            sh.INVESTIGATION_VERSION,sh.INVESTIGATION_STATUS,
            to_char(sh.SHORT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') SHORT_QUANTITY
            from RRL_CASE_PICK_SHORT sh join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=sh.CASE_PICK_TASK_ID
            where sh.CASE_PICK_SHORT_ID=:short_id""", {"short_id": short_id})
        if not rows:
            raise HTTPException(404, detail="Shortage incident not found")
        result = rows[0]
        instant=result.pop("created_instant",None)
        if instant:
            result["legacy_created_at"]=result["created_at"]
            result["created_at"]=datetime.fromisoformat(instant).astimezone(timezone.utc)
            result["time_basis"]="RECORDED_INSTANT"
        else:
            result["time_basis"]="LEGACY_CONFIGURED_OFFSET"
        cameras = self.gateway.fetch_all("""select VIEWPOINT_CODE,ARCHIVE_URI_TEMPLATE,STORED_TIME_OFFSET,
            BEFORE_SECONDS,AFTER_SECONDS,POLICY_VERSION from RRL_CCTV_VIEWPOINT
            where WARE_ID=:ware and CELL_CODE=:cell and ACTIVE=1 order by VIEWPOINT_CODE fetch first 21 rows only""",
            {"ware": result["warehouse"], "cell": result["cell"]})
        if len(cameras) > 20:
            raise HTTPException(409, detail="INCIDENT_CAMERA_BOUND_20")
        links = []
        for camera in cameras:
            try:
                uri = archive_uri(camera["archive_uri_template"], camera["stored_time_offset"], result["created_at"],
                    result["cell"], camera["viewpoint_code"], camera["before_seconds"], camera["after_seconds"])
                links.append({"viewpoint": camera["viewpoint_code"], "uri": uri, "policy_version": camera["policy_version"]})
            except ValueError:
                links.append({"viewpoint": camera["viewpoint_code"], "reason": "INVALID_CAMERA_CONFIGURATION"})
        events = self.gateway.fetch_all("""select CASE_PICK_EVENT_ID,CREATED_AT,CREATED_BY,PAYLOAD_JSON
            from RRL_CASE_PICK_EVENT where CASE_PICK_LINE_ID=:line_id and EVENT_TYPE='INVESTIGATION_REVIEWED'
            order by CASE_PICK_EVENT_ID desc fetch first 51 rows only""", {"line_id": result["case_pick_line_id"]})
        if len(events) > 50:
            raise HTTPException(409, detail="INCIDENT_REVIEW_HISTORY_BOUND_50")
        history = []
        for event in events:
            data = payload(event.pop("payload_json"))
            if data.get("short_id") == short_id:
                history.append({**event, **data["request"], "result": data["result"]})
        return {**result, "cameras": links, "history": history,
                "camera_state": "CONFIGURED" if cameras else "CAMERA_NOT_CONFIGURED"}

    def camera_settings(self,warehouse: int,cell: str)->list[dict[str,Any]]:
        rows=self.gateway.fetch_all("""select VIEWPOINT_CODE,ARCHIVE_URI_TEMPLATE,STORED_TIME_OFFSET,BEFORE_SECONDS,
            AFTER_SECONDS,ACTIVE,POLICY_VERSION from RRL_CCTV_VIEWPOINT where WARE_ID=:ware and CELL_CODE=:cell
            order by VIEWPOINT_CODE fetch first 101 rows only""",{"ware":warehouse,"cell":cell})
        if len(rows)>100:raise HTTPException(409,detail="CAMERA_CONFIGURATION_BOUND_100")
        return rows

    def configure(self, request: Any, actor: str) -> dict[str, Any]:
        try:
            if len(request.archive_uri_template.encode('utf-8'))>2000:raise ValueError('Archive template exceeds 2000 UTF-8 bytes')
            validate_template(request.archive_uri_template, request.stored_time_offset)
        except ValueError as exc:
            raise HTTPException(422, detail=str(exc)) from exc
        with stock_configuration_transaction(self.gateway, "Configure CCTV archive bookmark", actor, "warehouse_settings_edit") as cursor:
            cursor.execute("select count(*) from RRL_WARES where ID=:ware",{"ware":request.warehouse})
            if cursor.fetchone()[0]!=1:raise HTTPException(409,detail="Warehouse missing or ambiguous")
            cursor.execute("select count(*) from RRL_CELLS where WARE_ID=:ware and CELL=:cell",
                {"ware": request.warehouse, "cell": request.cell})
            if cursor.fetchone()[0] != 1:
                raise HTTPException(409, detail="Configure an unambiguous existing warehouse cell")
            cursor.execute("""select POLICY_VERSION from RRL_CCTV_VIEWPOINT
                where WARE_ID=:ware and CELL_CODE=:cell and VIEWPOINT_CODE=:viewpoint for update""",
                {"ware": request.warehouse, "cell": request.cell, "viewpoint": request.viewpoint})
            old = cursor.fetchone()
            version = int(old[0]) if old else 0
            if version != request.expected_version:
                raise HTTPException(409, detail="Camera configuration changed; reload")
            cursor.execute("""merge into RRL_CCTV_VIEWPOINT d using(select :ware WARE_ID,:cell CELL_CODE,:viewpoint VIEWPOINT_CODE from dual)s
                on(d.WARE_ID=s.WARE_ID and d.CELL_CODE=s.CELL_CODE and d.VIEWPOINT_CODE=s.VIEWPOINT_CODE)
                when matched then update set ARCHIVE_URI_TEMPLATE=:uri,STORED_TIME_OFFSET=:p_offset,
                    BEFORE_SECONDS=:p_before,AFTER_SECONDS=:p_after,ACTIVE=:active,POLICY_VERSION=:version,UPDATED_AT=systimestamp,UPDATED_BY=:actor
                when not matched then insert(WARE_ID,CELL_CODE,VIEWPOINT_CODE,ARCHIVE_URI_TEMPLATE,STORED_TIME_OFFSET,
                    BEFORE_SECONDS,AFTER_SECONDS,ACTIVE,POLICY_VERSION,UPDATED_BY)
                    values(s.WARE_ID,s.CELL_CODE,s.VIEWPOINT_CODE,:uri,:p_offset,:p_before,:p_after,:active,:version,:actor)""",
                {"ware": request.warehouse, "cell": request.cell, "viewpoint": request.viewpoint,
                 "uri": request.archive_uri_template, "p_offset": request.stored_time_offset,
                 "p_before": request.before_seconds, "p_after": request.after_seconds,
                 "active": int(request.active), "version": version + 1, "actor": actor})
        return {"warehouse": request.warehouse, "cell": request.cell, "viewpoint": request.viewpoint, "version": version + 1}

    def review(self, short_id: int, request: Any, actor: str) -> dict[str, Any]:
        if request.video_uri:
            try:
                validate_uri(request.video_uri)
            except ValueError as exc:
                raise HTTPException(422, detail=str(exc)) from exc
        body = request.model_dump(mode="json")
        with self.gateway.transaction("Review existing shortage incident") as cursor:
            entered = False
            try:
                cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,'case_pick_short_approve');end;", {"actor": actor})
                entered = True
                cursor.execute("""select EVENT_TYPE,CREATED_BY,PAYLOAD_JSON from RRL_CASE_PICK_EVENT
                    where OFFLINE_EVENT_ID=:event_id""", {"event_id": request.offline_event_id})
                old = cursor.fetchone()
                if old:
                    if old[0] != "INVESTIGATION_REVIEWED" or old[1] != actor:
                        raise HTTPException(409,detail="INVESTIGATION_EVENT_CONTENT_CONFLICT")
                    saved = payload(old[2].read() if hasattr(old[2], "read") else old[2])
                    if old[0] != "INVESTIGATION_REVIEWED" or old[1] != actor or saved.get("short_id") != short_id or saved.get("request") != body:
                        raise HTTPException(409, detail="INVESTIGATION_EVENT_CONTENT_CONFLICT")
                    return saved["result"]
                cursor.execute("""select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,INVESTIGATION_VERSION
                    from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:short_id for update""", {"short_id": short_id})
                short = cursor.fetchone()
                if short is None:
                    raise HTTPException(404, detail="Shortage incident not found")
                if short[2] != request.expected_version:
                    raise HTTPException(409, detail="INVESTIGATION_VERSION_CHANGED")
                result = {"short_id": short_id, "version": int(short[2]) + 1, "status": request.status}
                wire = json.dumps({"short_id": short_id, "request": body, "result": result}, ensure_ascii=False, sort_keys=True)
                if len(wire.encode("utf-8")) > 3900:
                    raise HTTPException(422, detail="Review exceeds the existing immutable event contract")
                cursor.execute("""update RRL_CASE_PICK_SHORT set INVESTIGATION_STATUS=:status,INVESTIGATION_VERSION=:version
                    where CASE_PICK_SHORT_ID=:short_id""", {"status": request.status, "version": result["version"], "short_id": short_id})
                cursor.execute("""insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,
                    EVENT_TYPE,OFFLINE_EVENT_ID,MESSAGE_TEXT,PAYLOAD_JSON,CREATED_AT,CREATED_BY)
                    values(RRL_CASE_PICK_EVENT_SQ.nextval,:task_id,:line_id,'INVESTIGATION_REVIEWED',:event_id,:note,:p_payload,systimestamp,:actor)""",
                    {"task_id": short[0], "line_id": short[1], "event_id": request.offline_event_id,
                     "note": request.note, "p_payload": wire, "actor": actor})
                return result
            finally:
                if entered:
                    cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
