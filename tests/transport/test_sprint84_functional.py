"""Sprint 84: READY_PERC column in routes tab trips table."""


def _src():
    return open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()


def test_routes_table_has_percent_header():
    src = _src()
    # Find the routes-tab table header section (after routeBriefMode heading)
    idx = src.index("dispatch-routes-table-wrap")
    snippet = src[idx : idx + 2000]
    assert '% сборки' in snippet or "% сборки" in snippet, "% header missing in routes tab"


def test_routes_table_has_readiness_bar_cell():
    src = _src()
    idx = src.index("dispatch-routes-table-wrap")
    snippet = src[idx : idx + 6000]
    assert "ReadinessBar" in snippet, "ReadinessBar missing in routes tab"
    assert "task.READY_PERC" in snippet


def test_colspan_updated_to_16():
    src = _src()
    assert "routeBriefMode ? 8 : 16" in src, "colSpan not updated from 15 to 16"


def test_brief_mode_colspan_unchanged():
    src = _src()
    assert "routeBriefMode ? 8 : 16" in src
