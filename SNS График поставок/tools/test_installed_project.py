"""Run using only the Python included in a fresh installation."""
import hashlib
import http.client
import io
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import threading
import time
import urllib.request
from contextlib import closing

install = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(install))
import server
import project_xml
import database_xml

with tempfile.TemporaryDirectory(prefix='http-check-', dir=install / 'runtime') as temp:
    temp = Path(temp)
    server.DB = temp / 'schedule.sqlite3'
    shutil.copy2(install / 'runtime/schedule.sqlite3', server.DB)
    httpd = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = 'http://127.0.0.1:' + str(httpd.server_port)
    try:
        times = []
        for _ in range(3):
            started = time.perf_counter()
            with urllib.request.urlopen(base + '/data/october.json') as response:
                assert response.read() == (install / 'data/october.json').read_bytes()
            times.append(round((time.perf_counter() - started) * 1000, 1))
        for url in ('/site/', '/site/drinks.html', '/site/tobacco.html', '/site/vendor/leaflet/leaflet.js', '/api/schedule?chain=drinks'):
            with urllib.request.urlopen(base + url) as response:
                assert response.status == 200
        export = temp / 'complete.xml'
        started = time.perf_counter()
        with urllib.request.urlopen(base + '/api/database.xml', timeout=180) as response, export.open('wb') as output:
            assert response.headers['Content-Type'].startswith('application/xml')
            shutil.copyfileobj(response, output)
        export_seconds = round(time.perf_counter() - started, 2)
        connection = http.client.HTTPConnection('127.0.0.1', httpd.server_port, timeout=180)
        started = time.perf_counter()
        connection.putrequest('POST', '/api/database.xml')
        connection.putheader('Content-Type', 'application/xml')
        connection.putheader('Content-Length', str(export.stat().st_size))
        connection.endheaders()
        with export.open('rb') as stream:
            while chunk := stream.read(1024 * 1024):
                connection.send(chunk)
        response = connection.getresponse()
        result = json.loads(response.read())
        assert response.status == 200, result
        connection.close()
        import_seconds = round(time.perf_counter() - started, 2)
        assert result['files'] == 35 and result['count'] == 19
        assert Path(result['backup']).is_file()
        imported_times = []
        for _ in range(3):
            started = time.perf_counter()
            with urllib.request.urlopen(base + '/data/october.json') as response:
                assert response.read() == (install / 'data/october.json').read_bytes()
            imported_times.append(round((time.perf_counter() - started) * 1000, 1))
        with urllib.request.urlopen(base + '/data/trip_details.json') as response:
            assert response.read() == (install / 'data/trip_details.json').read_bytes()
        with closing(sqlite3.connect(server.DB)) as db:
            assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
            assert db.execute('SELECT COUNT(*) FROM project_files').fetchone()[0] == 35
        report = {'portable_runtime': sys.version, 'http_round_trip': True, 'files': result['files'],
                  'recommendations': result['count'], 'backup_created': True,
                  'xml_bytes': export.stat().st_size, 'export_seconds': export_seconds, 'import_seconds': import_seconds,
                  'october_bytes': (install / 'data/october.json').stat().st_size,
                  'before_import_ms': times, 'after_import_ms': imported_times,
                  'environment': 'loopback, bundled Python, three sequential GETs before/after import; not Oracle throughput'}
        (install.parent.parent / 'reports/installed-project-check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(report), flush=True)
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join()
