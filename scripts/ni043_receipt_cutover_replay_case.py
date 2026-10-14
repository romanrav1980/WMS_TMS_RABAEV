"""Replay one original SAP receipt through the extracted single-writer boundary."""
import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.infrastructure.receiving import Receiving
from app.oracle_gateway import OracleGateway
s=get_settings();operation="REUSE.SAP.RECEIVE:cdbf4c0962"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 q.execute("select CANONICAL_REQUEST,RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=operation)
 row=q.fetchone();assert row,"Original source required"
 request,expected=map(read_oracle_json,row)
 q.execute("select count(*)from RRL_EVENTS");before=q.fetchone()[0]
 result=Receiving(OracleGateway()).receive(request["source"]["order_id"],
     {**request["metadata"],"operation_id":operation},request["actor"])
 assert result==expected,(result,expected)
 q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()[0]==before
 print("PASS138 original SAP receipt replay same saved result; extracted metadata booking has no posting method; physical journal unchanged",flush=True)
