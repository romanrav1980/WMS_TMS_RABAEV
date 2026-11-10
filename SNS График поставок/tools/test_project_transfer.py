"""Verify complete project transfer and transactional rejection of corrupt XML."""
import hashlib
import io
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import database_xml
import project_xml
import server


def manifest(db, root):
    return {name: (len(content), hashlib.sha256(content).hexdigest()) for name, content in project_xml.assets(db, root)}


with tempfile.TemporaryDirectory(prefix='xml-check-', dir=ROOT / 'runtime') as folder:
    folder = Path(folder)
    server.DB = folder / 'source.sqlite3'
    source = server.connect()
    live = Path(os.environ['LOCALAPPDATA']) / 'SNS Delivery Schedule/runtime/schedule.sqlite3'
    with sqlite3.connect(live) as original:
        original.backup(source)
    project_xml.init(source)
    source.commit()
    server.DB = folder / 'destination.sqlite3'
    target = server.connect()
    expected = manifest(source, ROOT)
    with tempfile.TemporaryFile() as xml:
        source.execute('BEGIN')
        project_xml.export(source, ROOT, xml)
        source.rollback()
        size = xml.tell()
        xml.seek(0)
        result = project_xml.restore(target, xml, server.valid_value, server.CHAINS)
    assert manifest(target, folder) == expected
    assert database_xml.serialize(source) == database_xml.serialize(target)
    assert target.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    with tempfile.TemporaryFile() as xml:
        project_xml.export(target, folder, xml)
        xml.seek(0)
        project_xml.restore(target, xml, server.valid_value, server.CHAINS)
    assert manifest(target, folder) == expected
    # Small snapshot tests fail after a deletion/insert, not just before a transaction.
    fixture = folder / 'fixture'
    (fixture / 'data').mkdir(parents=True)
    values = {'october': {'records': []}, 'trip_details': {}, 'planned_delivery': [], 'rc_districts': []}
    for name, value in values.items():
        (fixture / f'data/{name}.json').write_text(json.dumps(value), encoding='utf-8')
    empty = sqlite3.connect(':memory:')
    source.backup(empty)
    empty.execute('DELETE FROM project_files')
    empty.commit()
    small = io.BytesIO()
    project_xml.export(empty, fixture, small)
    good = small.getvalue()
    schedule_before = database_xml.serialize(target)
    for invalid in [good[:-30], good.replace(b'sha256="', b'sha256="BAD', 1),
                    good.replace(b'data/october.json', b'../server.py'),
                    good.replace(b'encoding="zlib-base64"', b'encoding="unknown"', 1),
                    b'<!DOCTYPE sns_project [<!ENTITY x "test">]>' + good]:
        try:
            project_xml.restore(target, io.BytesIO(invalid), server.valid_value, server.CHAINS)
            raise AssertionError('Corrupt snapshot accepted')
        except ValueError:
            pass
        assert manifest(target, folder) == expected
        assert database_xml.serialize(target) == schedule_before
    project_xml.restore(target, io.BytesIO(database_xml.serialize(source)), server.valid_value, server.CHAINS)
    assert manifest(target, folder) == expected  # Legacy XML must keep project datasets.
    report = {'files': len(expected), 'source_bytes': sum(v[0] for v in expected.values()),
              'xml_bytes': size, 'recommendations': target.execute('SELECT COUNT(*) FROM schedule_recommendations').fetchone()[0],
              'full_round_trip': True, 'second_round_trip': True, 'corruption_rollback': True, 'legacy_xml': True}
    (ROOT / 'reports/project-transfer-check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report), flush=True)
    empty.close()
    source.close()
    target.close()
