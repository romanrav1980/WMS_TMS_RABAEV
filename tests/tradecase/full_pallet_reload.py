"""Recheck the restored physical full pallet and issue a new loading intent."""
import json
import os
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection

if __name__=='__main__':
    path=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07/full-pallet-reload.json';s=json.loads(path.read_text(encoding='utf-8'))
    assert s['warehouse_id']==221164919 and s['unload_stage']=='PASS'
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    def save():path.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
    try:
        if 'reloaded'not in s:
            if 'old_load_replay_after_unload'not in s:
                value=expect(200,http('POST','/api/transport/loading/confirm-single',s['load_body']));assert value==s['loaded'];s['old_load_replay_after_unload']=value
                with oracle_connection()as c:
                    q=c.cursor();q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p and CELL=:c',p=s['carrier'],c=s['load_body']['scan_cell']);assert q.fetchone()==(10,10)
                save()
            if 'reload_body'not in s:
                v=expect(200,http('GET','/api/transport/loading/single-preview?shipment_identifier='+s['st_pallet']))
                s['reload_body']=dict(s['load_body'],operation_id='TFP22.RELOAD.1219',expected_version=v['expected_version'],expected_composition_signature=v['composition_signature'],measurements=dict(s['load_body']['measurements'],content_version=v['expected_version']));save()
            if 'reload_before_qc'not in s:
                s['reload_before_qc']=http('POST','/api/transport/loading/confirm-single',s['reload_body']);save();assert s['reload_before_qc'][0]==409 and 'CONTROL_REQUIRED'in str(s['reload_before_qc'])
            base='/api/outgoing-quality/'+s['st_pallet']
            if 'reload_qc_body'not in s:
                v=expect(200,http('GET',base));assert not v['ready'];s['reload_quality_before']=v
                s['reload_qc_body']=dict(s['fullpal_qc_body'],operation_id='TFP22.RELOAD.QC.1219',expected_composition_signature=v['composition_signature']);save()
            if 'reload_qc'not in s:s['reload_qc']=expect(200,http('POST',base+'/scan',s['reload_qc_body']));save()
            assert expect(200,http('POST',base+'/scan',s['reload_qc_body']))==s['reload_qc']
            s['reloaded']=expect(200,http('POST','/api/transport/loading/confirm-single',s['reload_body']));save()
        assert expect(200,http('POST','/api/transport/loading/confirm-single',s['reload_body']))==s['reloaded']
        with oracle_connection()as c:
            q=c.cursor();q.execute('select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=s['warehouse_id']);assert q.fetchone()==(0,0)
            q.execute('select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:o',o=s['reload_body']['operation_id']);assert q.fetchone()[0]==-10
        s['reload_stage']='PASS';print(json.dumps(dict(status='PASS',stock=[0,0],operation=s['reload_body']['operation_id'],old_replay_did_not_reload=True)))
    finally:s['http']+=CALLS;save()
