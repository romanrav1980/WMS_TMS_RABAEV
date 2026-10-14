"""Metadata-only camera bookmark/review/replay on our completed shortage fixture16."""
import sys,json
from pathlib import Path
from uuid import uuid4
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.short_investigation import ShortInvestigation
from app.modules.inventory.api.investigation_routes import CameraInput,InvestigationInput
from fastapi import HTTPException
g=OracleGateway();svc=ShortInvestigation(g);short_id=16;tag=uuid4().hex[:10]
context=svc.read(short_id)
assert context["cell"]=="QP74b8056265" and context["warehouse"]==1,"Only our known fixture16 is authorized"
before=g.fetch_all("select nvl(sum(REMAIN),0) P,nvl(sum(HARD_RESERVED_BASE),0) H from RRL_REMAINS")[0]
camera=CameraInput(warehouse=1,cell=context["cell"],viewpoint="QA-"+tag,expected_version=0,
 archive_uri_template="https://nvr.invalid/archive?view={viewpoint}&cell={cell}&from={from_iso}&to={to_iso}")
cfg=svc.configure(camera,"admin")
try:
 read=svc.read(short_id)
 link=next(x for x in read["cameras"] if x["viewpoint"]==camera.viewpoint)
 assert "from=" in link["uri"] and "%2B03%3A00" in link["uri"],link
 request=InvestigationInput(expected_version=context["investigation_version"],offline_event_id="INV.QA:"+tag,
  status="CLOSED",note="QA archive bookmark and immutable review; no quantity correction",video_uri=link["uri"])
 first=svc.review(short_id,request,"admin");assert svc.review(short_id,request,"admin")==first
 try:svc.review(short_id,request.model_copy(update={"note":"Different contents"}),"admin");raise AssertionError("Changed replay accepted")
 except HTTPException as exc:assert exc.status_code==409
 try:svc.review(short_id,request.model_copy(update={"offline_event_id":"INV.QA.STALE:"+tag}),"admin");raise AssertionError("Stale version accepted")
 except HTTPException as exc:assert exc.status_code==409
 after=g.fetch_all("select nvl(sum(REMAIN),0) P,nvl(sum(HARD_RESERVED_BASE),0) H from RRL_REMAINS")[0]
 assert before==after
 assert len([r for r in svc.read(short_id)["history"] if r["offline_event_id"]==request.offline_event_id])==1
 print(json.dumps({"passed":True,"short_id":short_id,"version":first["version"],"case":"configured archive time window; review/replay/conflicts; P/H unchanged; no video network call"}),flush=True)
finally:
 svc.configure(camera.model_copy(update={"expected_version":cfg["version"],"active":False}),"admin")
 print("Own dummy archive viewpoint disabled; immutable review retained",flush=True)
