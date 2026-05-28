"""Sprint 71: Sticky thead in trips table (.dispatch-trips-table-wrap)."""
import pytest


def test_sticky_trips_thead_css():
    css = open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()
    assert ".dispatch-trips-table-wrap .dispatch-grid thead th" in css
    assert "position: sticky" in css[css.index(".dispatch-trips-table-wrap .dispatch-grid thead th"):]


def test_sprint71_marker():
    css = open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()
    assert "Sprint 71" in css
