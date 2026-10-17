"""Publication boundary: no native/private articles, accounts or cached grants in offline bundle."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = {"using-help", "access-model", "operation-recovery"}


def test_offline_copy_contains_only_reviewed_public_publication():
    source = json.loads((ROOT / "docs/help/published.json").read_text(encoding="utf-8-sig"))
    bundle = json.loads((ROOT / "admin/wms_admin_frontend/src/features/platform/help/offline-public.json").read_text(encoding="utf-8"))
    expected = [row for row in source if row["article_id"] in ALLOWLIST]
    assert {row["article_id"] for row in bundle} == ALLOWLIST
    assert all(not row.get("required_permissions") for row in expected)
    assert bundle == expected
    assert all(set(row["related"]) <= ALLOWLIST for row in bundle)
