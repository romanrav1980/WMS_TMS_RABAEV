"""QC ten synthetic source codes through the real outgoing scan command; no flag DML."""
import json
import os
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS

if __name__=='__main__':
    path=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T07/full-pallet.json'
    state=json.loads(path.read_text(encoding='utf-8'))
    source=json.loads((ROOT/'runtime/test-evidence/tradecase/2026-10-21/T06/scoped-full-preparation.json').read_text(encoding='utf-8'))
    assert state['warehouse_id']==source['fixture']['warehouse_id']==220639789
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    def save():path.write_text(json.dumps(state,indent=2,default=str),encoding='utf-8')
    try:
        base='/api/outgoing-quality/'+state['st_pallet']
        if 'fullpal_qc_body'not in state:
            current=expect(200,http('GET',base))
            state['fullpal_qc_body']=dict(operation_id='TFP22.QC.1221',expected_composition_signature=current['composition_signature'],error_count=0,scans=source['receipt_proof']['codes']);save()
        if 'fullpal_qc'not in state:
            state['fullpal_qc']=expect(200,http('POST',base+'/scan',state['fullpal_qc_body']));save()
        assert expect(200,http('POST',base+'/scan',state['fullpal_qc_body']))==state['fullpal_qc']
        current=expect(200,http('GET',base));assert current['ready'];state['fullpal_quality']=current
        print(json.dumps(dict(ready=current['ready'],count=current['physical_unit_count'])))
    finally:state['http']+=CALLS;save()
