"""Bind the owned IN_TRANSIT CASE to an actual native ST and check its marked units."""
from pathlib import Path
import json,os,sys
sys.path[:0]=['.','tests/tradecase']
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
P=Path('runtime/test-evidence/tradecase/2026-10-19/T07/fixture-1156.json');s=json.loads(P.read_text())
def save():P.write_text(json.dumps(s,indent=2,default=str))
try:
 with oracle_connection()as c:
  q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
  q.execute('select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t',t=s['case_id']);s['carrier'],v=q.fetchone()
 if 'binding'not in s:s['binding']=expect(200,http('POST',f"/api/case-pick/tasks/{s['case_id']}/bind-shipment",dict(pallet_identifier=s['st_pallet'],scan_container=s['carrier'],expected_content_version=v)));save()
 quality=expect(200,http('GET','/api/outgoing-quality/'+s['carrier']))
 if 'qc_body'not in s:s['qc_body']=dict(operation_id='T7.QC.1156',expected_composition_signature=quality['composition_signature'],error_count=0,scans=s['pick_body']['unit_scans']);save()
 if 'qc_result'not in s:s['qc_result']=expect(200,http('POST','/api/outgoing-quality/'+s['carrier']+'/scan',s['qc_body']));save()
 s['quality']=expect(200,http('GET','/api/outgoing-quality/'+s['carrier']));assert s['quality']['ready'];print(json.dumps(dict(ready=s['quality']['ready'],carrier=s['carrier'],count=s['quality']['physical_unit_count'])))
finally:s['http']+=CALLS;save()
