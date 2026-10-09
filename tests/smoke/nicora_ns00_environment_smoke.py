"""Author's live Oracle negative probes for NS00; run after core seed."""
from __future__ import annotations
import json
from pathlib import Path
from unittest.mock import patch
from tools.nicora_environment import oracle_fixture as f
from tools.nicora_environment.fixture_plan import ROOT,plan
from tools.nicora_environment.probe import api,write_report

EVIDENCE = ROOT/'runtime/test-evidence/nicora_ns00'
MANIFEST = EVIDENCE/'fixture-manifest.json'


def fingerprint() -> str:
    with f.oracle_connection() as connection:
        cursor=connection.cursor()
        actual={table:f.owned(cursor,table,rows) for table,rows in plan().items()}
        return f.digest(actual)


def main() -> None:
    results=[]
    before=fingerprint()
    try:
        f.seed_reset(EVIDENCE/'missing-provenance'/'manifest.json',reset=True)
        raise AssertionError('Unowned existing keys were accepted')
    except RuntimeError as exc:
        assert 'provenance' in str(exc),str(exc)
        assert fingerprint()==before
        results.append({'case':'missing_provenance','status':'PASS_REFUSED_UNCHANGED'})
    api('/api/admin/product-shipment-settings/DS-BASE-D10',
        {'shipment_aging_hours':4,'shipment_aging_comment':'NS00 dirty-key negative probe'})
    dirty=fingerprint()
    try:
        f.seed_reset(MANIFEST,reset=True)
        raise AssertionError('Changed fixture was accepted')
    except RuntimeError as exc:
        assert 'changed' in str(exc),str(exc)
        assert fingerprint()==dirty
        results.append({'case':'changed_owned_row','status':'PASS_REFUSED_UNCHANGED'})
    finally:
        api('/api/admin/product-shipment-settings/DS-BASE-D10',
            {'shipment_aging_hours':0,'shipment_aging_comment':'NS00 baseline'})
    assert fingerprint()==before
    original=f.templates
    def fail_second_table(name: str) -> dict[str,str]:
        values=original(name)
        if name=='seed.sql':
            values['RRL_CELLS']=values['RRL_CELLS'].replace(':X','(cast(null as number)+:X)')
        return values
    try:
        with patch.object(f,'templates',side_effect=fail_second_table):
            f.seed_reset(MANIFEST,reset=True)
        raise AssertionError('Injected NOT NULL violation did not fail')
    except Exception as exc:
        assert 'ORA-01400' in str(exc),str(exc)
        assert fingerprint()==before
        results.append({'case':'failure_after_delete_and_first_insert','status':'PASS_ATOMIC_ROLLBACK','error':'ORA-01400'})
    write_report(EVIDENCE/'negative-probes.json',{'role':'author_checks_not_independent_review',
                 'tests':results,'fixture_sha256_before_after':before})
    write_report(EVIDENCE/'negative-probes-sql.json',f.METRICS)
    print(json.dumps(results))


if __name__=='__main__':
    main()
