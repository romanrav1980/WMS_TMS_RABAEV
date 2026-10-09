from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.check_architecture import ROOT, python_records
from tools.architecture.rules import compare_debt, cycles, import_rules
from api.wms_api_server.app.modules.transport.public import normalize_transport_type

POLICY = json.loads((ROOT / 'config/architecture/nicora-policy.json').read_text(encoding='utf-8'))
BASE = 'api/wms_api_server/app/'


class BoundaryTests(unittest.TestCase):
    def test_domain_cannot_import_http_or_database(self):
        source = BASE + 'modules/transport/domain/rules.py'
        self.assertIn('new-module-to-legacy-internal', import_rules(source, BASE + 'db.py', POLICY))
        self.assertIn('domain-outward-dependency', import_rules(source, BASE + 'modules/transport/api/routes.py', POLICY))

    def test_application_uses_ports_not_concrete_adapter(self):
        source = BASE + 'modules/transport/application/assign.py'
        self.assertIn('application-outward-dependency', import_rules(source, BASE + 'modules/transport/infrastructure/oracle.py', POLICY))
        self.assertEqual(import_rules(source, BASE + 'modules/transport/application/ports.py', POLICY), [])

    def test_other_module_can_use_facade_but_not_private_domain(self):
        source = BASE + 'modules/fulfillment/application/ship.py'
        self.assertEqual(import_rules(source, BASE + 'modules/transport/public.py', POLICY), [])
        self.assertIn('cross-module-private-import', import_rules(source, BASE + 'modules/transport/domain/rules.py', POLICY))

    def test_frontend_cross_feature_requires_public_export(self):
        source = 'admin/wms_admin_frontend/src/features/transport/ui/Trip.tsx'
        self.assertEqual(import_rules(source, 'admin/wms_admin_frontend/src/features/inventory/index.ts', POLICY), [])
        self.assertIn('cross-feature-private-import', import_rules(source, 'admin/wms_admin_frontend/src/features/inventory/ui/Stock.tsx', POLICY))

    def test_router_database_and_reverse_dependency_are_rejected(self):
        self.assertIn('router-direct-database-import', import_rules(BASE + 'routers/x.py', BASE + 'oracle_gateway.py', POLICY))
        self.assertIn('service-to-router', import_rules(BASE + 'services/x.py', BASE + 'routers/x.py', POLICY))

    def test_cycles_identified_without_flagging_shared_leaf(self):
        self.assertEqual(cycles({'a': {'b'}, 'b': {'c'}, 'c': set()}), [])
        self.assertEqual(cycles({'a': {'b'}, 'b': {'a', 'leaf'}, 'leaf': set()}), [{'a', 'b'}])

    def test_growth_and_reintroduction_are_rejected(self):
        baseline = {'entries': {'large': {'maximum': 700}}}
        regressions, stale = compare_debt(Counter({'large': 701, 'new-edge': 1}), baseline)
        self.assertEqual(set(regressions), {'large', 'new-edge'})
        self.assertEqual(stale, [])
        self.assertEqual(compare_debt(Counter(), baseline)[1], ['large'])
        self.assertIn('large', compare_debt(Counter({'large': 700}), {'entries': {}})[0])

    def test_relative_and_fully_qualified_imports_are_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            app = root / POLICY['python_root']
            files = {'__init__.py': '', 'db.py': '', 'modules/transport/domain/rules.py':
                     'from ....db import connect\nfrom api.wms_api_server.app.db import other\nimport importlib\nimportlib.import_module("app.db")\n'}
            for name, content in files.items():
                target = app / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding='utf-8')
            records = python_records(root, POLICY)
            record = next(item for item in records if item['path'].endswith('rules.py'))
            self.assertEqual([item['target'] for item in record['imports']].count(BASE + 'db.py'), 3)

    def test_domain_external_dependency_and_untyped_function_are_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            app = root / POLICY['python_root']
            file = app / 'modules/transport/domain/rules.py'
            file.parent.mkdir(parents=True)
            file.write_text('from fastapi import HTTPException\ndef f(x):\n    return x\n', encoding='utf-8')
            violations = python_records(root, POLICY)[0]['violations']
            self.assertTrue(any(item.startswith('domain-external-dependency:fastapi') for item in violations))
            self.assertIn('new-module-untyped-function:f', violations)

    def test_type_only_import_does_not_form_runtime_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            app = root / POLICY['python_root']
            app.mkdir(parents=True)
            (app / 'a.py').write_text('from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from .b import X\n', encoding='utf-8')
            (app / 'b.py').write_text('from .a import X\n', encoding='utf-8')
            records = python_records(root, POLICY)
            graph = {r['path']: {i['target'] for i in r['imports'] if not i['typeOnly']} for r in records}
            self.assertEqual(cycles(graph), [])

    def test_typescript_alias_exports_and_type_only_imports_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / 'frontend'
            (project / 'src').mkdir(parents=True)
            (project / 'tsconfig.json').write_text(json.dumps({'compilerOptions': {'baseUrl': '.', 'paths': {'@/*': ['src/*']}}, 'include': ['src']}), encoding='utf-8')
            (project / 'src/a.ts').write_text('import type { B } from "@/b";\nexport { value } from "./b";\n', encoding='utf-8')
            (project / 'src/b.ts').write_text('export interface B {}\nexport const value = 1;\n', encoding='utf-8')
            result = subprocess.run(['node', str(ROOT / 'tools/architecture/frontend_graph.cjs'), str(root), 'frontend', str(ROOT / 'admin/wms_admin_frontend')], capture_output=True, text=True, encoding='utf-8', check=True)
            records = json.loads(result.stdout)
            self.assertEqual(len(records), 2)
            imports = next(r for r in records if r['path'].endswith('a.ts'))['imports']
            self.assertEqual([i['typeOnly'] for i in imports], [True, False])
            self.assertTrue(all(i['target'] == 'frontend/src/b.ts' for i in imports))


class TransportRuleTests(unittest.TestCase):
    def test_optional_and_existing_type_values_keep_legacy_behavior(self):
        for value, expected in [(None, None), (' Газель ', '5'), ('ГАЗЕЛЬ', '5'), (' 7 ', '7'), (' other ', 'other'), (' ', '')]:
            with self.subTest(value=value):
                self.assertEqual(normalize_transport_type(value), expected)

    def test_service_keeps_its_existing_entry_point(self):
        from api.wms_api_server.app.services.transport_service import _normalize_transtype
        self.assertIs(_normalize_transtype, normalize_transport_type)



class BaselineCliTests(unittest.TestCase):
    def test_tighten_cannot_authorize_new_debt(self):
        from unittest.mock import patch
        from scripts import check_architecture as checker
        with tempfile.TemporaryDirectory() as tmp:
            baseline = Path(tmp) / 'debt.json'
            original = json.dumps({'entries': {'old': {'maximum': 1, 'owner': 'owner', 'reason': 'legacy', 'remediation': 'extract'}}})
            baseline.write_text(original, encoding='utf-8')
            with patch.object(checker, 'collect', return_value=(Counter({'old': 1, 'new': 1}), {'files': 2}, [])), patch('sys.argv', ['check', '--baseline', str(baseline), '--report', str(Path(tmp) / 'report.json'), '--tighten-baseline']):
                self.assertEqual(checker.main(), 1)
            self.assertEqual(baseline.read_text(encoding='utf-8'), original)

    def test_paid_down_allowance_is_removed_and_cannot_return(self):
        from unittest.mock import patch
        from scripts import check_architecture as checker
        with tempfile.TemporaryDirectory() as tmp:
            baseline = Path(tmp) / 'debt.json'
            baseline.write_text(json.dumps({'entries': {'old': {'maximum': 1, 'owner': 'owner', 'reason': 'legacy', 'remediation': 'extract'}}}), encoding='utf-8')
            arguments = ['check', '--baseline', str(baseline), '--report', str(Path(tmp) / 'report.json')]
            with patch.object(checker, 'collect', return_value=(Counter(), {'files': 1}, [])), patch('sys.argv', arguments + ['--tighten-baseline']):
                self.assertEqual(checker.main(), 0)
            with patch.object(checker, 'collect', return_value=(Counter({'old': 1}), {'files': 1}, [])), patch('sys.argv', arguments):
                self.assertEqual(checker.main(), 1)

if __name__ == '__main__':
    unittest.main()
