"""Real localhost API smoke; credentials remain in process memory and are never printed."""
import json,os,re,secrets,sys
from pathlib import Path
from uuid import uuid4
import httpx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"api/wms_api_server"),str(ROOT/"scripts")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

def main():
    basic=os.environ.get("VITE_ADMIN_BASIC_AUTH")
    if not basic:
        match=re.search(r'VITE_ADMIN_BASIC_AUTH=([^"\r\n]+)',(ROOT/"front.bat").read_text(encoding="utf-8-sig"))
        if not match:raise RuntimeError("Configured API account required")
        basic=match.group(1)
    prefix="akh"+uuid4().hex[:8];actor=prefix+"user";password=secrets.token_urlsafe(24)
    gateway=OracleGateway();checks=[]
    with gateway.transaction("metadata.http.fixture") as cursor:
        cursor.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'HTTP fixture',:password,'NONE',1,0,1)",{"id":actor,"password":password})
    try:
        with httpx.Client(base_url="http://127.0.0.1:8088",timeout=30) as client:
            assert client.get("/api/access/me").status_code==401
            client.auth=tuple(basic.split(":",1))
            for path in ("/api/access/catalog","/api/access/groups","/api/access/objects?kind=WAREHOUSE","/api/access/assignments","/api/knowledge/spaces","/api/knowledge/articles","/api/help/articles/using-help"):
                response=client.get(path);assert response.status_code==200,(path,response.status_code,response.text[:300])
            assignments=client.get("/api/access/assignments?username=ADMIN").json()
            for item in assignments:
                for field in ("valid_from","valid_until","revoked_at"):
                    if item[field] is not None: assert item[field].endswith("+00:00"),(field,item[field])
            assert client.get("/api/access/objects?kind=WAREHOUSE&query=1").json()
            checks.append("admin_read_contracts")
            checks.append("timezone_aware_assignment_timestamps")
            body=dict(operation_id=prefix+":role",command_type="ROLE_SAVE",payload=dict(role_id=prefix,title="HTTP fixture",permissions=["fixture_read"],active=True,expected_version=0))
            response=client.post("/api/access/commands",json=body);assert response.status_code==200,response.text
            assert client.post("/api/access/commands",json=body).json()["replayed"] is True
            body["payload"]["title"]="changed"
            assert client.post("/api/access/commands",json=body).status_code==409
            assert client.get("/api/access/commands/"+prefix+":role").status_code==200
            checks.append("http_command_receipt_and_conflict")
            client.auth=(actor,password)
            own=client.get("/api/access/me");assert own.status_code==200 and own.json()["username"]==actor
            assert client.get("/api/access/catalog").status_code==403
            assert client.post("/api/access/commands",json=body).status_code==409 # same op belongs to another actor
            assert client.get("/api/access/commands/"+prefix+":role").status_code==404
            assert client.get("/api/help/articles/using-help").status_code==200
            assert client.get("/api/knowledge/articles/using-help/history").status_code==403
            checks.append("ordinary_user_denials_and_public_help")
    finally:
        with gateway.transaction("metadata.http.cleanup") as cursor:
            cursor.execute("delete from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=:id",{"id":prefix})
            cursor.execute("delete from RRL_ACCESS_ROLE where ROLE_ID=:id",{"id":prefix})
            cursor.execute("delete from RRL_ACCESS_AUDIT where OPERATION_ID=:id",{"id":prefix+":role"})
            cursor.execute("delete from RRL_PLATFORM_COMMAND where DOMAIN='ACCESS' and OPERATION_ID=:id",{"id":prefix+":role"})
            cursor.execute("delete from RUSERS where ID=:id",{"id":actor})
    result=dict(status="PASS",checks=checks,fixture_cleaned=True,stock_effect="NONE")
    (ROOT/"reports/retailcase/2026-10-14/access-knowledge/http-smoke.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result))
if __name__=="__main__":main()
