"""Root-run bounded READ ONLY baseline; no API calls or Oracle writes."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/retailcase/2026-10-15/warehouse-empty-scoped/history-before.json'
QUERIES={
 'requests':"select REQUEST_ID,rawtohex(sys.dbms_crypto.hash(SOURCE_JSON,:hash_algorithm))SOURCE_HASH,SNAPSHOT_SHA256,rawtohex(sys.dbms_crypto.hash(CAPTURE_CONTEXT,:hash_algorithm))CONTEXT_HASH from RRL_WH_WEIGH_REQUEST order by REQUEST_ID fetch first 1001 rows only",
 'claims':"select CLAIM_ID,REQUEST_ID,DEVICE_ID,CLAIMED_BY,rawtohex(sys.dbms_crypto.hash(SOURCE_JSON,:hash_algorithm))SOURCE_HASH from RRL_WH_WEIGH_CLAIM order by CLAIM_ID fetch first 1001 rows only",
 'zeros':"select CLAIM_ID,REQUEST_ID,ZERO_SOURCE_SHA256,PROFILE_SHA256,rawtohex(sys.dbms_crypto.hash(SOURCE_JSON,:hash_algorithm))SOURCE_HASH,rawtohex(sys.dbms_crypto.hash(RESULT_JSON,:hash_algorithm))RESULT_HASH from RRL_WH_WEIGH_ZERO order by CLAIM_ID fetch first 1001 rows only",
 'captures':"select CAPTURE_KEY,SOURCE_SHA256,rawtohex(sys.dbms_crypto.hash(RESULT_JSON,:hash_algorithm))RESULT_HASH from RRL_WH_SCALE_CAPTURE order by CAPTURE_KEY fetch first 1001 rows only",
 'device':"select DEVICE_ID,WARE_ID,POST_CELL,ACTIVE_FLAG,DEVICE_MODE,POLICY_VERSION,CALIBRATION_REF,SENDER_ID,MEASUREMENT_BASIS,CALIBRATED_UNTIL from RRL_WH_SCALE_DEVICE where DEVICE_ID='WHREQ15.SCALE'",
 'sender':"select ID,nvl(DELETED,0)DELETED,WARE_ID,USER_GROUP,RRL_HAS_WRIGHT(ID,'warehouse_scale_ingest')INGEST from RUSERS where ID='WHREQ15.GW'",
 'case':"select CASE_PICK_TASK_ID,SSCC,WARE_ID,PALLET_TYPE_ID,CONTENT_VERSION,STATUS,PICKED_QTY,ASSIGNED_TO,RESOURCE_SESSION_ID,ASSIGNED_RESOURCE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1139",
 'session':"select *from RRL_RESOURCE_SESSION where SESSION_ID=59",
 'active_device_claims':"select CLAIM_ID,REQUEST_ID,CLAIMED_BY,CREATED_AT,EXPIRES_AT from RRL_WH_WEIGH_CLAIM where DEVICE_ID='WHREQ15.SCALE'and EXPIRES_AT>=systimestamp fetch first 21 rows only",
 'active_device_assembly':"select SESSION_ID,CASE_PICK_TASK_ID,STATE,OPERATOR_ID,EXPIRES_AT from RRL_ASSEMBLY_SESSION where DEVICE_ID='WHREQ15.SCALE'and STATE in('OPEN','BLOCKED','HOLD')fetch first 21 rows only"}


def main():
 p=argparse.ArgumentParser();p.add_argument('--capture',action='store_true');args=p.parse_args()
 if not args.capture:print(json.dumps(QUERIES,indent=2));return
 assert not OUT.exists(),'Never overwrite before images'
 sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
 from stock_posting_environment import load_local_oracle_environment
 load_local_oracle_environment()
 from app.db import oracle_connection
 from app.db import rows_as_dicts
 with oracle_connection()as connection:
  c=connection.cursor()
  try:
   import oracledb
   algorithm=c.var(oracledb.DB_TYPE_NUMBER)
   c.execute('begin :value := sys.dbms_crypto.hash_sh256; end;',value=algorithm)
   actual_algorithm=algorithm.getvalue()
   c.execute('set transaction read only');c.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");who=c.fetchone();assert who[0]=='RABAEV'and who[1].lower()=='orcl'
   result={'status':'READ_ONLY_BASELINE','schema':who[0],'service':who[1],'queries':QUERIES}
   for key,sql in QUERIES.items():
    c.execute(sql,{'hash_algorithm':actual_algorithm}if ':hash_algorithm'in sql else {});result[key]=rows_as_dicts(c)
    assert len(result[key])<=1000
  finally:connection.rollback()
 OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open('x',encoding='utf-8')as stream:json.dump(result,stream,indent=2,default=str)
 print(json.dumps({'status':'CAPTURED_READ_ONLY','path':str(OUT),'counts':{k:len(result[k])for k in QUERIES}}))
if __name__=='__main__':main()
