"""C-0172: the route screens take the zone of the trip's local source values from confirmed data only (time approval and store
cards) and print each moment with its own offset. Runs the real TypeScript helper through Node (type stripping) on fixture inputs."""
import json
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HELPER = ROOT / "admin/wms_admin_frontend/src/features/integrations/tradecase/routeZone.ts"
CASES = json.loads((ROOT / "tests/fixtures/tradecase_route_zone.json").read_text(encoding="utf-8"))
RUNNER = """
const input = JSON.parse(require('fs').readFileSync(0, 'utf8'));
import(process.argv[1]).then(m => {
  const zones = input.cases.map(c => { const r = m.sourceZone(c.context); return { zone: r.zone, basis: r.basis, reason: r.reason }; });
  const stamps = input.stamps.map(([iso]) => m.stamp(iso));
  process.stdout.write(JSON.stringify({ zones, stamps }));
});
"""


@pytest.fixture(scope="module")
def results():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required to run the TypeScript helper")
    run = subprocess.run([node, "--experimental-strip-types", "--no-warnings", "-e", RUNNER, HELPER.as_uri()], input=json.dumps(CASES),
                         capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


def test_source_zone_from_confirmed_data_only(results):
    for case, actual in zip(CASES["cases"], results["zones"]):
        assert actual == case["expect"], case["name"]


def test_moment_keeps_its_own_offset(results):
    assert results["stamps"] == [expected for _, expected in CASES["stamps"]]
