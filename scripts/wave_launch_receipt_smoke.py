"""Minimal durable launch receipt: wrong wave and other author never prove rollback."""
import json,re,secrets,sys
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4
import httpx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

def main():
 g=OracleGateway();actor='rc'+uuid4().hex[:11];password=secrets.token_urlsafe(24);checks=[]
 basic=re.search(r'VITE_ADMIN_BASIC_AUTH=([^"\r\n]+)',(ROOT/'front.bat').read_text(encoding='utf-8-sig')).group(1).split(':',1)
 source=g.fetch_all("""select OPERATION_ID,json_value(CANONICAL_REQUEST,'$.source.wave_id' returning number) WAVE
  from RRL_STOCK_OPERATION where COMMAND_TYPE='WAVE_LAUNCH'and ACTOR=:actor and STATE='APPLIED'
  order by CREATED_AT desc fetch first 1 rows only""",{'actor':basic[0]})[0]
 wave=int(source['wave']);op=source['operation_id'];url=f'/api/picking/waves/{wave}/launch-receipts/'+quote(op,safe='')
 try:
  with g.transaction('Receipt reader identity fixture')as c:
   c.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'Receipt fixture',:password,'NONE',1,0,1)",id=actor,password=password)
  with httpx.Client(base_url='http://127.0.0.1:8088',timeout=30)as c:
   assert c.get(url).status_code==401
   c.auth=tuple(basic)
   r=c.get(url);assert r.status_code==200,r.text[:300]
   value=r.json();assert value['state']=='APPLIED'and value['launch_outcome_confirmed']is True
   assert value['wave_status'] in('LAUNCHED','CANCELLED','DONE','COMPLETED','CLOSED','PREVIEW')
   if not value['continuation_steps']:
    assert value['continuation_state']in('PENDING','RECONCILIATION_REQUIRED')
   elif value['continuation_state']=='COMPLETE':
    assert len(value['continuation_steps'])==7 and all(step['state']=='DONE'for step in value['continuation_steps'])
   assert set(value)=={'operation_id','wave_id','wave_status','state','launch_outcome_confirmed','continuation_state','continuation_steps','commands_executed'}
   checks.append('original_launch_receipt_minimal_and_continuation_not_invented')
   r=c.get(f'/api/picking/waves/{wave+1}/launch-receipts/'+quote(op,safe=''));assert r.json()['state']=='NOT_VISIBLE'
   checks.append('receipt_bound_to_original_wave')
   c.auth=(actor,password)
   r=c.get(url);assert r.status_code==200,r.text[:300]
   assert r.json()['state']=='NOT_VISIBLE'and r.json()['launch_outcome_confirmed']is False
   checks.append('other_author_no_grants_cannot_read_original_receipt')
 finally:
  with g.transaction('Receipt identity fixture cleanup')as c:c.execute('delete from RUSERS where ID=:actor',actor=actor)
 result=dict(status='PASS',checks=checks,fixture_cleaned=True,business_rows='READ_ONLY',stock_effect='NONE')
 (ROOT/'reports/retailcase/2026-10-15/resource-timeline/launch-receipt-native.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
