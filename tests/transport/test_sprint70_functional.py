"""Sprint 70: Select-all / deselect-all toolbar for trip STs."""
import pytest


def test_sprint70_toolbar_present():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert "Sprint 70" in src, "Sprint 70 marker missing"
    assert "dispatch-trip-sts-toolbar" in src, "toolbar div missing"
    assert "dispatch-trip-selall-btn" in src, "select-all button class missing"


def test_select_all_sets_all_st_numbers():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    idx = src.index("Sprint 70")
    snippet = src[idx : idx + 700]
    assert "taskSts.map(s => s.ST_NUMBER)" in snippet, "select-all does not use taskSts"
    assert "new Set()" in snippet, "deselect-all (empty Set) missing"


def test_toolbar_css_defined():
    css = open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()
    assert ".dispatch-trip-sts-toolbar" in css
    assert ".dispatch-trip-selall-btn" in css


def test_typescript_compiles():
    import subprocess
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd="admin/wms_admin_frontend",
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
