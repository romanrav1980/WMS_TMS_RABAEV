"""Offline analysis probes: no API, Oracle or source-file writes. Print JSON."""
import ast
import copy
from datetime import date
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT / 'api/wms_api_server'))
from app.services import vrp_solver as s
from app.services.transport_service import TransportService

v = s.VrpVehicle(1, 'TEST', 'DRY', 20, 10)
o = s.VrpOrder('ST', 'A', 41.7, 44.8, 1, 100, 1, 'COLD', 0, 1, True, 30)
p = s.solve([o], [v], solver='savings')
z = s.solve([s.VrpOrder('ZERO', 'Z', 0, 44.8, 1, 100, 1, None)], [v], solver='savings')
tree = ast.parse(Path(s.__file__).read_text(encoding='utf-8'))
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_solve_ortools')
loads = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
stores = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
report = {'mode': 'offline only', 'savings': {'incompatible_type_and_impossible_window_assigned': bool(p.routes), 'tw_violations': p.tw_violations, 'duration': p.routes[0].total_duration_min, 'zero_coordinate_lost': not z.routes and not z.unassigned}, 'ortools_installed': importlib.util.find_spec('ortools') is not None, 'static_unbound_n_orders': 'n_orders' in loads - stores - {a.arg for a in fn.args.args}}

class Gateway:
    def fetch_all(self, *a, **kw):
        return [{'PLAN_JSON': json.dumps({'routes': [{'vehicle_num': 'TEST', 'vehicle_id': 1, 'stops': ['ST']}]}), 'SOLVER': 'savings'}]
    def execute(self, *a, **kw):
        return 1

class Service(TransportService):
    def __init__(self):
        self.gateway, self.created, self.fail = Gateway(), 0, False
    def create_task(self, *a, **kw):
        self.created += 1
        return self.created
    def update_task(self, *a, **kw):
        pass
    def assign_sts(self, *a, **kw):
        if self.fail:
            raise RuntimeError('injected failure')
        return {'assigned': 1}

t = Service()
t.apply_vrp_plan(1, date(2026, 9, 15))
t.apply_vrp_plan(1, date(2026, 9, 15))
report['fake_gateway_reapply_created'] = t.created
t = Service()
t.fail = True
try:
    t.apply_vrp_plan(1, date(2026, 9, 15))
except Exception as exc:
    report['fake_gateway_failure'] = {'type': type(exc).__name__, 'create_called': t.created}

spec = importlib.util.spec_from_file_location('nv', PACKAGE / 'tools/validate_nikora_xml_profile.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
E, B, N = m.E, m.BASE, '{' + m.N + '}'
manifest = json.loads((B / 'vendor-manifest.json').read_text(encoding='utf-8'))
report['vendor_files'] = len(manifest['files'])
report['vendor_hash_mismatches'] = [f['local'] for f in manifest['files'] if hashlib.sha256((B / f['local']).read_bytes()).hexdigest() != f['sha256']]
report['positive'] = [{'file': f.name, 'errors': m.validate(E.parse(str(f), m.PARSER).getroot())} for f in sorted((B / 'examples').glob('*.xml'))]
agg = E.parse(str(B / 'examples/11-aggregation-event.xml'), m.PARSER).getroot()
agg.find('.//' + N + 'eventCode').text = 'DISAGGREGATED'
for e in agg.findall(N + 'subject'):
    e.set('role', 'OUTPUT' if e.get('role') == 'INPUT' else 'INPUT')
if len(agg.findall(N + 'subject[@role="OUTPUT"]')) < 2:
    extra = copy.deepcopy(agg.find(N + 'subject[@role="OUTPUT"]'))
    body = '13333333000000348'
    digit = (-sum(int(c) * (3 if i % 2 == 0 else 1) for i, c in enumerate(reversed(body)))) % 10
    extra.set('sscc', body + str(digit))
    agg.insert(list(agg).index(agg.find(N + 'huRelation')), extra)
    rel = copy.deepcopy(agg.find(N + 'huRelation'))
    rel.set('childSSCC', extra.get('sscc'))
    agg.insert(list(agg).index(agg.find(N + 'huRelation')) + 1, rel)
report['split_one_to_many'] = {'xsd_valid': m.schema(agg).validate(agg), 'errors': m.validate(agg)}
import contextlib
import io
from unittest.mock import patch
captured = io.StringIO()
with patch.object(Path, 'write_text', return_value=0), contextlib.redirect_stdout(captured):
    m.main()
report['negative'] = json.loads(captured.getvalue())['negative']
print(json.dumps(report, indent=2))
