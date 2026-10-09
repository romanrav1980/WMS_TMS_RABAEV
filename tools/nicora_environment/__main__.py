"""NS00 fixture CLI. Invocations never recreate the RABAEV schema."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
from uuid import uuid4
from .fixture_plan import ROOT
from .oracle_fixture import seed_reset,acknowledge_owned_change,serial,METRICS
from .probe import assertions,readiness,api,fact,markers,sql_review,write_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['seed','reset','cleanup','verify','record-fact','verify-restart','mark','sql-review'])
    parser.add_argument('--evidence',type=Path,default=ROOT/'runtime/test-evidence/nicora_ns00')
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    if not evidence.is_relative_to(ROOT):
        raise ValueError('Evidence/provenance must remain in the project workspace')
    manifest = evidence/'fixture-manifest.json'
    if args.action in {'seed','reset','cleanup'}:
        result = seed_reset(manifest,reset=args.action=='reset',cleanup=args.action=='cleanup')
        write_report(evidence/(args.action+'-result.json'),result)
        print(json.dumps({'status':result['status'],'rows':result['rows']}))
    elif args.action=='verify':
        result = {'readiness':readiness(),'fixture':assertions()}
        write_report(evidence/'verify.json',result)
        print('PASS_LIVE_ORACLE_API')
    elif args.action=='record-fact':
        value = 'NS00 restart '+str(uuid4())
        api('/api/admin/product-shipment-settings/DS-BASE-D10',
            {'shipment_aging_hours':3,'shipment_aging_comment':value})
        recorded = fact()
        if recorded['shipment_aging_comment']!=value or recorded['shipment_aging_hours']!=3:
            raise RuntimeError('Committed fact did not match request')
        acknowledge_owned_change(manifest)
        write_report(evidence/'restart-before.json',{'fact':recorded,'readiness':readiness(),
                     'recorded_at':datetime.now(timezone.utc).isoformat()})
        print('FACT_COMMITTED_AND_READ_BACK')
    elif args.action=='verify-restart':
        before = json.loads((evidence/'restart-before.json').read_text(encoding='utf-8'))
        after = {'fact':fact(),'readiness':readiness(),'fixture':assertions()}
        if before['fact']!=after['fact']:
            raise RuntimeError('Committed fact lost or changed across restart')
        after['status'] = 'PASS_FACT_PERSISTENCE'
        write_report(evidence/'restart-after.json',after)
        print(after['status'])
    elif args.action=='mark':
        write_report(evidence/'sql-start.json',markers())
        print('SQL_MARKER_SAVED')
    else:
        start = json.loads((evidence/'sql-start.json').read_text())
        result = sql_review(start)
        write_report(evidence/'sql-review.json',result)
        print('SQL_REVIEW_SAVED')
    write_report(evidence/(args.action+"-sql.json"),METRICS)
    return 0


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(type(exc).__name__+': '+str(exc),file=sys.stderr)
        raise SystemExit(1)
