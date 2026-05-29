"""Sprint 69: Delete key to bulk-unassign selected trip STs."""
import pytest


def test_delete_handler_present():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    idx = src.index("Sprint 69")
    snippet = src[idx : idx + 1200]
    assert 'e.key === "Delete"' in snippet, "Delete key handler missing"
    assert "handleBulkUnassign" in snippet, "handleBulkUnassign not called on Delete"


def test_no_duplicate_tag_const():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    # The keydown handler should not have two const tag declarations
    idx = src.index("Sprint 44")
    handler_block = src[idx : idx + 1600]
    assert handler_block.count("const tag") <= 1, "Duplicate const tag in keydown handler"


def test_bulk_unassign_button_tooltip():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert 'title="Delete"' in src, "Delete tooltip not on bulk-unassign button"


def test_typescript_compiles():
    from tests.support.frontend_checks import run_tsc_no_emit
    r = run_tsc_no_emit()
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
