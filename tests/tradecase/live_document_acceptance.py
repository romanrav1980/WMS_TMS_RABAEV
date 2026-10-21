"""Owner-authorized local Oracle/HTTP acceptance; owns only freshly named metadata fixtures."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import base64
import json
import os
from pathlib import Path
import secrets
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.mcp.tms_mcp_server import oracle_connection

EVIDENCE = ROOT / "runtime/test-evidence/tradecase/2026-10-19/T02"
CALLS = []
BASE = "http://127.0.0.1:8088"


def http(method, path, body=None, actor=None, password=None):
    actor = actor or os.environ["TRADECASE_ADMIN_USER"]
    password = password or os.environ["TRADECASE_ADMIN_PASSWORD"]
    auth = base64.b64encode((actor + ":" + password).encode()).decode()
    request = Request(BASE + path, data=json.dumps(body).encode() if body is not None else None,
                      headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"}, method=method)
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=35) as response:
            code, raw = response.status, response.read()
    except HTTPError as exc:
        code, raw = exc.code, exc.read()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = {"raw_response": raw.decode("utf-8", errors="replace")[:1000]}
    CALLS.append(dict(method=method, path=path, status=code, elapsed_ms=round((time.perf_counter()-started)*1000, 2), response=value))
    return code, value


def expect(status, actual):
    assert actual[0] == status, actual
    return actual[1]


def make_fixture():
    suffix = uuid4().hex[:10]
    actor, role, password = "TC19" + suffix, "TC19" + suffix, secrets.token_hex(24)
    ware = 190000000 + secrets.randbelow(10000000)
    with oracle_connection() as conn:
        cur = conn.cursor()
        cur.execute("select user,sys_context('USERENV','DB_NAME'),sys_context('USERENV','SERVICE_NAME') from dual")
        assert cur.fetchone() == ("RABAEV", "ORCL", "orcl")
        cur.execute("select count(*) from RRL_WARES where ID in (:a,:b)", a=ware, b=ware+1)
        assert cur.fetchone()[0] == 0
        for identifier in (ware, ware+1):
            cur.execute("insert into RRL_WARES(ID,NAME) values(:id,:name)", id=identifier, name="TC19-QA-"+str(identifier))
            cur.execute("insert into RRL_ACCESS_OBJECT(KIND,OBJECT_ID,TITLE,ACTIVE,VERSION_NO) values('WAREHOUSE',:id,:name,1,1)", id=str(identifier), name="TRADECASE QA")
        cur.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED) values(:id,:pwd,'TRADECASE acceptance','TC19QA',:ware,0)", id=actor, pwd=password, ware=ware)
        cur.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO) values(:id,'TRADECASE QA',1,1)", id=role)
        for permission in ("tradecase_view", "tradecase_import"):
            cur.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION) values(:id,:p)", id=role, p=permission)
        cur.execute("""insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)
            values(:id,:actor,:role,'WAREHOUSE',:ware,'CURRENT',systimestamp-interval '1' minute,systimestamp+interval '12' hour,'admin','Isolated TRADECASE acceptance',1)""",
                    id=role, actor=actor, role=role, ware=str(ware))
        cur.execute("select nvl(max(LOG_ID),0) from RRL_SQL_SLOW_LOG")
        slow_marker = cur.fetchone()[0]
        cur.execute("select count(*) from RRL_PALLETS")
        physical_before = cur.fetchone()[0]
        conn.commit()
    return dict(warehouse_id=ware, foreign_warehouse_id=ware+1, actor=actor, role=role,
                password=password, slow_marker=slow_marker, physical_before=physical_before)


def run(fixture):
    ware, actor, password = fixture["warehouse_id"], fixture["actor"], fixture["password"]
    path = f"/api/tradecase/warehouses/{ware}"
    setting = dict(operation_id="setup", expected_version=0, source_id="SAP_QA", active_skm="SAP_QA",
                   planning_source="SAP", enabled=True, reason="Isolated metadata acceptance")
    expect(200, http("PUT", path+"/site", setting))
    assert expect(200, http("PUT", path+"/site", setting))["replayed"]
    expect(403, http("PUT", path+"/site", setting, actor, password))
    expect(200, http("GET", path+"/site", actor=actor, password=password))
    expect(403, http("GET", f"/api/tradecase/warehouses/{ware+1}/site", actor=actor, password=password))
    def envelope(identifier, payload, version=1):
        return dict(schema_version=1,event_id=uuid4().hex,source_id="SAP_QA",warehouse_id=ware,
                    document_id=identifier,version=version,occurred_at=datetime.now(timezone.utc).isoformat(),payload=payload)
    def send(body):
        return http("POST", "/api/tradecase/messages", body, actor, password)
    for identifier in ("SNS", "BLC"):
        expect(200, send(envelope(identifier, dict(entity_type="OWNER",title=identifier))))
    expect(200, send(envelope("A",dict(entity_type="SKU",title="Product A",units_per_box=10,permitted_mrc=["200"]))))
    expect(200, send(envelope("C1",dict(entity_type="RECIPIENT",title="Recipient C1",target_owner_id="BLC",
        permitted_source_owners=["SNS"],buyout_mode="BEFORE_PICK",lead_time_days=1,min_osg_days=50))))
    line=dict(line_id="10",sku_id="A",source_owner_id="SNS",target_owner_id="BLC",mrc="200",quantity="25",uom="BOX",min_osg_days=50)
    order=dict(entity_type="ORDER",recipient_id="C1",planned_ship_at="2026-10-19T12:00:00+03:00",lines=[line])
    missing=envelope("BAD",deepcopy(order));missing["payload"]["lines"][0]["sku_id"]="UNKNOWN"
    assert expect(200,send(missing))["status"]=="WAITING"
    expect(404,http("GET",path+"/documents/ORDER/BAD",actor=actor,password=password))
    rejected=expect(200,http("GET",path+"/messages/"+missing["event_id"],actor=actor,password=password))
    assert rejected["result"]["status"]=="WAITING" and rejected["request"]["document_id"]=="BAD"
    assert expect(200,send(missing))["status"]=="WAITING"
    page=expect(200,http("GET",path+"/messages?limit=1",actor=actor,password=password))
    assert len(page["items"])==1 and page["has_more"]
    # The native effect, receipt and outbox roll back together on caller failure.
    from api.wms_api_server.app.modules.integrations.contracts_tradecase import TradeEnvelope
    from api.wms_api_server.app.modules.integrations.infrastructure.tradecase_documents import OracleTradecaseDocuments
    from api.wms_api_server.app.transaction_gateway import TransactionGateway
    rolled=envelope("ROLLBACK",dict(entity_type="OWNER",title="Rollback proof"))
    with oracle_connection() as conn:
        answer=OracleTradecaseDocuments(TransactionGateway(conn.cursor())).receive(TradeEnvelope.model_validate(rolled),actor)
        conn.rollback()
    with oracle_connection() as conn:
        cur=conn.cursor()
        cur.execute("select count(*) from RRL_TRADE_DOCUMENT where WARE_ID=:w and EXTERNAL_ID='ROLLBACK'",w=ware)
        assert cur.fetchone()[0]==0
        cur.execute("select count(*) from RRL_TRADE_MESSAGE where WARE_ID=:w and EVENT_ID=:id",w=ware,id=rolled["event_id"])
        assert cur.fetchone()[0]==0
        cur.execute("select count(*) from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id",id=answer["outbox_id"])
        assert cur.fetchone()[0]==0
    original=envelope("O1",order)
    expect(200,send(original));assert expect(200,send(original))["replayed"]
    alias=deepcopy(original);alias["event_id"]=uuid4().hex
    assert expect(200,send(alias))["replayed"]
    conflict=deepcopy(original);conflict["payload"]["lines"][0]["quantity"]="26"
    assert "EVENT_CONTENT_CONFLICT" in expect(409,send(conflict))["detail"]["code"]
    changed=envelope("O1",deepcopy(order),2);changed["payload"]["lines"][0]["quantity"]="30"
    expect(200,send(changed))
    stale=deepcopy(original);stale["event_id"]=uuid4().hex
    assert "STALE_VERSION" in expect(409,send(stale))["detail"]["code"]
    trip=dict(entity_type="TRIP",vehicle_id="V1",planning_source="SAP",planned_departure_at="2026-10-19T12:00:00+03:00",
              capacity_kg="8000",capacity_m3="66",orders=[dict(order_id="O1",line_id="10",quantity="30")])
    def trip_send(identifier): return send(envelope(identifier,trip))
    with ThreadPoolExecutor(max_workers=2) as pool:
        values=list(pool.map(trip_send,["R1","R2"]))
    assert sorted(code for code,_ in values)==[200,409],values
    assert "ORDER_QUANTITY_ALREADY_ASSIGNED" in next(value for code,value in values if code==409)["detail"]["code"]
    expect(200,http("GET",path+"/documents/ORDER?limit=1",actor=actor,password=password))
    detail=expect(200,http("GET",path+"/documents/ORDER/O1",actor=actor,password=password))
    assert detail["document_version"]==2 and detail["payload"]["lines"][0]["quantity"]=="30"
    own=envelope("O2",order)
    with ThreadPoolExecutor(max_workers=2) as pool: same=list(pool.map(send,[own,own]))
    assert all(code==200 for code,_ in same) and sum(bool(v["replayed"]) for _,v in same)==1,same
    cancelled=envelope("O2",dict(order,cancelled=True),2);expect(200,send(cancelled))
    assert "CANCELLED_DOCUMENT_REQUIRES_NEW_ID" in expect(409,send(envelope("O2",order,3)))["detail"]["code"]
    with oracle_connection() as conn:
        cur=conn.cursor();cur.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:id",id=fixture["role"]);conn.commit()
    expect(403,send(original))
    with oracle_connection() as conn:
        cur=conn.cursor();cur.execute("select count(*) from RRL_PALLETS");assert cur.fetchone()[0]==fixture["physical_before"]
        cur.execute("select count(*) from user_objects where status='INVALID' and object_name not like 'BIN$%'");assert cur.fetchone()[0]==0
        cur.execute("select count(*) from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='TRIP'",w=ware);assert cur.fetchone()[0]==1
        cur.execute("select count(*) from RRL_TRADE_MESSAGE m where WARE_ID=:w and SOURCE_ID='SAP_QA' and not exists(select 1 from RRL_EVENT_OUTBOX o where o.EVENT_OUTBOX_ID=json_value(m.RESULT_JSON,'$.outbox_id' returning number))",w=ware)
        assert cur.fetchone()[0]==0
        cur.execute("select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 30 rows only",n=fixture["slow_marker"])
        return [list(row) for row in cur]


if __name__=="__main__":
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    previous=EVIDENCE/"document-acceptance.json"
    if previous.exists(): previous.rename(EVIDENCE/("document-acceptance-"+uuid4().hex[:8]+".json"))
    fixture=make_fixture();safe={k:v for k,v in fixture.items() if k!="password"}
    (EVIDENCE/"fixture.json").write_text(json.dumps(safe,indent=2),encoding="utf-8")
    try:
        slow=run(fixture)
        report=dict(status="PASS",fixture=safe,calls=CALLS,slow_sql=slow,physical_stock_changed=False,
                    limits=["Metadata-only; no real SAP/ITMS/L4 connection", "No legal-owner inventory admission yet"])
    except Exception as exc:
        report=dict(status="FAIL",error=str(exc),fixture=safe,calls=CALLS)
        raise
    finally:
        with oracle_connection() as conn:
            cur=conn.cursor()
            cur.execute("update RUSERS set DELETED=1 where ID=:actor and USER_GROUP='TC19QA'",actor=fixture["actor"])
            cur.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp) where ASSIGNMENT_ID=:id and USERNAME=:actor",id=fixture["role"],actor=fixture["actor"])
            conn.commit()
        if "report" in locals(): (EVIDENCE/"document-acceptance.json").write_text(json.dumps(report,indent=2,ensure_ascii=True,default=str),encoding="utf-8")
    print(json.dumps(dict(status=report["status"],http_calls=len(CALLS),warehouse_id=safe["warehouse_id"],slow_sql=slow)))
