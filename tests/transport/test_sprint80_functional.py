"""Sprint 80: NAPR (direction) column in available STs table."""
import pytest


def test_napr_header_present():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert '"NAPR"' in src, "NAPR sort field missing"
    assert "Напр." in src, "Напр. header label missing"


def test_napr_cell_in_available_st_row():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    idx = src.index("function AvailableStRow")
    snippet = src[idx : idx + 3000]
    assert "dispatch-napr-badge" in snippet, "NAPR badge not in AvailableStRow"
    assert "st.NAPR" in snippet


def test_colspan_17():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert 'colSpan={17}' in src, "colSpan not updated to 17"


def test_napr_css():
    css = open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()
    assert ".dispatch-napr-badge" in css


def test_typescript_compiles():
    import subprocess
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd="admin/wms_admin_frontend",
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
