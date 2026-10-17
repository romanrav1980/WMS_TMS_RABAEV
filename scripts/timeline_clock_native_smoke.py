"""Existing historical approvals must not supply a current resource timeline clock."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.timeline_clock import current_timeline_clock

def main():
 g=OracleGateway();checks=[]
 with g.transaction('Native current timeline source READ ONLY')as c:
  c.execute('set transaction read only')
  for trip in (33564,33570):
   clock=current_timeline_clock(c,trip,'admin')
   assert clock['status']=='SOURCE_CHANGED'and clock['operations']=={}
   checks.append(dict(trip_id=trip,status=clock['status'],projected_operations=0))
  c.execute("select count(*)from user_objects where status='INVALID'");assert c.fetchone()[0]==0
 result=dict(status='PASS',checks=checks,business_rows='READ_ONLY',stock_effect='NONE',positive_current_approval_fixture='SEPARATE_CALLER_ROLLBACK_SMOKE: scripts/timeline_clock_positive_smoke.py')
 (ROOT/'reports/retailcase/2026-10-15/resource-timeline/approved-clock-native.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(result))
if __name__=='__main__':main()
