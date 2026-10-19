"""Native NEED stale versions, offset normalization and explicit source refresh of an expired snapshot."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,os,json,copy
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path('runtime/test-evidence/tradecase/2026-10-19/T09/need-revisions.json');assert not P.exists(),'Supplement already executed; do not resend new revisions'
f=json.loads(Path('runtime/test-evidence/tradecase/2026-10-19/T09/need-fixture.json').read_text());w=f['warehouse_id'];id=f['a_id'];base=f'/api/tradecase/warehouses/{w}';out={'checks':[]}
try:
 with oracle_connection()as c:q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
 current=expect(200,http('GET',base+'/documents/NEED/'+id));assert current['document_version']==5
 original=next(x for x in f['requests']if x['document_id']==id and x['version']==1);same=copy.deepcopy(original)
 def local(value):return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone(timedelta(hours=3))).isoformat()
 for key in ['snapshot_at','period_from','period_until']:same['payload'][key]=local(same['payload'][key])
 for supply in same['payload']['supplies']:supply['expected_at']=local(supply['expected_at'])
 repeat=expect(200,http('POST','/api/tradecase/messages',same));assert repeat['replayed'];out['checks']+=['same_event_offset_equivalence_keeps_original_receipt']
 old=copy.deepcopy(next(x for x in f['requests']if x['document_id']==id and x['version']==4));old['event_id']='T9.SUPPLEMENT.OLD4';r=expect(409,http('POST','/api/tradecase/messages',old));assert r['detail']['code']=='STALE_VERSION';out['checks']+=['old_revision_new_event_cannot_replace5']
 body=copy.deepcopy(original);body['payload']=copy.deepcopy(current['payload']);body.update(event_id='T9.SUPPLEMENT.UTC6',version=6)
 for key in ['snapshot_at','period_from','period_until']:body['payload'][key]=local(body['payload'][key])
 for supply in body['payload']['supplies']:supply['expected_at']=local(supply['expected_at'])
 expect(200,http('POST','/api/tradecase/messages',body));r=expect(200,http('GET',base+'/needs/'+id+'?max_age_minutes=60'));assert r['document_version']==6 and r['additional_boxes']=='40';out['checks']+=['new_revision_equivalent_period_offset_accepted']
 fresh=copy.deepcopy(body);fresh.update(event_id='T9.SUPPLEMENT.FRESH7',version=7);fresh['payload']['snapshot_at']=datetime.now(timezone.utc).isoformat();first=expect(200,http('POST','/api/tradecase/messages',fresh));again=expect(200,http('POST','/api/tradecase/messages',fresh));assert again['replayed']and again['outbox_id']==first['outbox_id']
 result=expect(200,http('GET',base+'/needs/'+id+'?max_age_minutes=60'));assert not result['expired']and result['document_version']==7 and result['additional_boxes']=='40';assert expect(200,http('GET',base+'/needs/'+f['b_id']+'?max_age_minutes=60'))['additional_boxes']=='30';out['checks']+=['source_refresh7_recalculates_fresh40','repeated_refresh_one_outbox','other_recipient30_preserved']
 out.update(status='PASS',current_a=result,request_refresh=fresh,limits='Synthetic source refresh, preview only; no proposal approval, stock or SAP topup created');print(json.dumps(dict(status=out['status'],checks=out['checks'])))
except Exception as e:out.update(status='FAIL',error=str(e));raise
finally:out['http']=CALLS;P.write_text(json.dumps(out,indent=2,default=str))
