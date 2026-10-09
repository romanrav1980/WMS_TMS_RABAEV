from __future__ import annotations
import contextlib
import io
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import install_nicora_skills as installer
from scripts import test_mcp_servers as smoke


class McpSmokeTests(unittest.TestCase):
    def test_endpoint_failures_are_not_healthy(self):
        self.assertEqual(smoke.routing_health({'osrm': {'error': 'offline'}, 'valhalla': {'status': 503}}),
                         {'osrm': False, 'valhalla': False})
        self.assertEqual(smoke.routing_health({}), {'osrm': False, 'valhalla': False})

    def test_successful_endpoints_are_reachable(self):
        self.assertTrue(all(smoke.routing_health({'osrm': {'status': 200}, 'valhalla': {'status': 200}}).values()))

    def test_mismatched_response_id_is_rejected(self):
        proc = SimpleNamespace(stdin=io.StringIO(), stdout=io.StringIO('{"jsonrpc":"2.0","id":9,"result":{}}\n'))
        with self.assertRaises(RuntimeError):
            smoke.rpc(proc, {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'})

    def test_request_timeout_does_not_hang(self):
        released = threading.Event()
        proc = SimpleNamespace(stdin=io.StringIO(), stdout=SimpleNamespace(readline=lambda: (released.wait(), '')[1]))
        try:
            with self.assertRaises(TimeoutError):
                smoke.rpc(proc, {'id': 1}, timeout=0.03)
        finally:
            released.set()

    def test_strict_routing_gate_fails_without_claiming_mcp_failure(self):
        def fake(kind, timeout):
            result = {'mcp': 'ok'}
            if kind == 'docker':
                result['endpoints'] = {'osrm': False, 'valhalla': True}
            return result
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / 'health.json'
            with patch.object(smoke, 'check_server', side_effect=fake), patch('sys.argv', ['smoke', '--require-routing', '--report', str(report)]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(smoke.main(), 1)
            import json
            content = json.loads(report.read_text(encoding='utf-8'))
            self.assertFalse(content['passed'])
            self.assertEqual(content['servers']['docker']['mcp'], 'ok')

    def test_non_strict_gate_reports_offline_routing_without_blocking_tools(self):
        with patch.object(smoke, 'check_server', return_value={'mcp': 'ok', 'endpoints': {'osrm': False, 'valhalla': False}}), patch('sys.argv', ['smoke']), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(smoke.main(), 0)


class SkillInstallTests(unittest.TestCase):
    def test_existing_different_skill_is_preserved_before_any_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            existing = target / installer.NAMES[0] / 'SKILL.md'
            existing.parent.mkdir()
            existing.write_text('local customization', encoding='utf-8')
            with patch('sys.argv', ['install', '--install', '--target', str(target)]), self.assertRaises(ValueError):
                installer.main()
            self.assertEqual(existing.read_text(encoding='utf-8'), 'local customization')
            self.assertFalse((target / installer.NAMES[1]).exists())

    def test_install_is_repeatable_and_copies_exact_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch('sys.argv', ['install', '--install', '--target', tmp]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(installer.main(), 0)
                self.assertEqual(installer.main(), 0)
            for name in installer.NAMES:
                self.assertEqual((Path(tmp) / name / 'SKILL.md').read_bytes(),
                                 (installer.ROOT / 'tools/skills' / name / 'SKILL.md').read_bytes())


if __name__ == '__main__':
    unittest.main()
