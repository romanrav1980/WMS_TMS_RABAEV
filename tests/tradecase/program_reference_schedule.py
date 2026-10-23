"""Read-only native calculation of the original program's fixed reference timetable, not a real road matrix."""
import sys,json,time
from copy import deepcopy
from pathlib import Path
sys.path[:0]=['scripts','.']
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
import oracledb
addresses=['REF.HUB','REF.BRANCH','REF.STORE'];durations=[60,40,30,60];windows=[('11:00:00','12:00:00'),('11:30:00','13:00:00'),('12:00:00','14:00:00')]
chain=['REF.DEPOT',*addresses,'REF.DEPOT']
source=dict(route_material=dict(policy_id='CURRENT_NATIVE_POLICY_WITH_CONTROLLED_PROGRAM_INPUT',depot_address=chain[0],order_valid=True,stops=addresses,legs=[dict(from_address=a,to_address=b,duration_min=t,duration_basis='ROAD_PROFILE_ESTIMATE',fresh=True,provider='CONTROLLED_PROGRAM_REFERENCE_NOT_LIVE_ROAD')for a,b,t in zip(chain,chain[1:],durations)]),members=[dict(address=a,delivery_window_from='2026-10-26 '+w[0],delivery_window_to='2026-10-26 '+w[1])for a,w in zip(addresses,windows)],destination_rules=[dict(address=a,unload_norm_min=15,window_strict=1,address_count=1)for a in addresses],operations=[dict(code='DRIVE',plan_start='2026-10-26 10:00:00',plan_end='2026-10-26 11:00:00'),dict(code='DRIVE_BACK',plan_start='2026-10-26 13:10:00',plan_end='2026-10-26 14:10:00')])
report=dict(kind='CONTROLLED_REFERENCE_NATIVE_READ_ONLY',reference='program.txt lines192-224, fixed minutes, not a live provider route',source=source,status='FAIL')
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute('set transaction read only');wire=q.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,json.dumps(source));result=q.var(oracledb.DB_TYPE_CLOB);start=time.perf_counter();q.callproc('RRL_TT_ROUTE_SCHEDULE.calculate',[wire,'Europe/Moscow',result]);report['elapsed_ms']=round((time.perf_counter()-start)*1000,2);raw=result.getvalue();raw=raw.read()if hasattr(raw,'read')else raw;report['result']=json.loads(raw);c.rollback()
 report['reference_expected']={'arrival_hhmm':['11:00','11:55','12:55'],'return_hhmm':'14:10'}
 actual=[x['arrival_at'][11:16]if x.get('arrival_at')else None for x in report['result'].get('stops',[])]
 report['matches_owner_approved_reference']=actual==report['reference_expected']['arrival_hhmm'] and report['result'].get('return_at','')[11:16]=='14:10' and report['result']['stops'][-1].get('service_finish_at','')[11:16]=='13:10' and report['result'].get('driver_breaks_included') is True
 report['status']='MATCH' if report['matches_owner_approved_reference'] and not report['result'].get('issues') else 'REFERENCE_MISMATCH'
 report['owner_decision']='2026-10-23: preserve120min driving/15min rest; store12:55, service complete13:10, return14:10. Raw source unchanged; no native rule changed'
 report['negative_checks']=[]
 for name in ('old_resource_envelope','missed_store_window'):
  negative=deepcopy(source)
  if name=='old_resource_envelope':
   negative['operations'][-1]['plan_end']='2026-10-26 13:55:00'
   expected_issue='ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE'
  else:
   negative['members'][-1]['delivery_window_to']='2026-10-26 12:40:00'
   expected_issue='DELIVERY_HARD_WINDOW_MISSED'
  with oracle_connection() as c:
   q=c.cursor();q.execute('set transaction read only')
   wire=q.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,json.dumps(negative))
   result=q.var(oracledb.DB_TYPE_CLOB)
   q.callproc('RRL_TT_ROUTE_SCHEDULE.calculate',[wire,'Europe/Moscow',result])
   raw=result.getvalue();raw=raw.read() if hasattr(raw,'read') else raw
   native=json.loads(raw);c.rollback()
  check=dict(case=name,expected_issue=expected_issue,result=native)
  check['matched']=expected_issue in {x.get('code') for x in native.get('issues',[])}
  report['negative_checks'].append(check)
 if not all(x['matched'] for x in report['negative_checks']):
  report['status']='NEGATIVE_CHECK_FAILED'

 print(json.dumps(dict(status=report['status'],return_at=report['result'].get('return_at'),stops=report['result'].get('stops'),issues=report['result'].get('issues'))))
except Exception as e:report['error']=str(e);raise
finally:
 p=Path('runtime/test-evidence/tradecase/2026-10-23/T09/program-reference-schedule-owner-approved.json')
 archive=p.with_name('program-reference-schedule-first.json')
 if p.exists()and not archive.exists():archive.write_bytes(p.read_bytes())
 p.write_text(json.dumps(report,indent=2),encoding='utf-8')

if report['status'] != 'MATCH':
 raise SystemExit(1)
