from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx"
CSS = ROOT / "admin/wms_admin_frontend/src/styles.css"


def test_available_st_table_has_windowed_rendering():
    source = PAGE.read_text(encoding="utf-8")
    assert "ST_VIRTUAL_THRESHOLD" in source
    assert "visiblePagedSts" in source
    assert "stVirtualTopPad" in source
    assert "stVirtualBottomPad" in source
    assert 'data-virtualized={viewMode === "flat" ? "true" : "false"}' in source


def test_available_st_virtualization_uses_react_virtual():
    """Sprint 102: пагинация заменена @tanstack/react-virtual."""
    source = PAGE.read_text(encoding="utf-8")
    # New implementation: react-virtual replaces manual pagination
    assert "useVirtualizer" in source
    assert "stRowVirtualizer" in source
    assert "getVirtualItems" in source
    assert "pagedSts = sortedSts" in source  # pagedSts now aliases sortedSts directly


def test_virtual_spacer_rows_have_no_table_padding():
    css = CSS.read_text(encoding="utf-8")
    assert ".dispatch-virtual-spacer td" in css
    assert "padding: 0 !important" in css


def test_2000_row_playwright_smoke_exists():
    source = (ROOT / "tests/ui/transport_table_2000_nfr_smoke.cjs").read_text(encoding="utf-8")
    assert "makeRows(2000)" in source
    assert 'data-virtualized") === "true"' in source
    assert "Too many rendered ST table rows" in source
    assert "Стр. 2 из 20" in source
