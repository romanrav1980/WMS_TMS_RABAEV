"""Sprint 78: Persist filter checkboxes (unassignedOnly/assembledOnly/notAssembledOnly) in localStorage."""
import pytest


def test_unassigned_only_reads_ls():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    idx = src.index("tms_unassignedOnly")
    # Should appear in both useState init AND in an effect
    assert src.count("tms_unassignedOnly") >= 2, "tms_unassignedOnly should be read and written"


def test_assembled_only_reads_ls():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert src.count("tms_assembledOnly") >= 2


def test_not_assembled_only_reads_ls():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert src.count("tms_notAssembledOnly") >= 2


def test_sprint78_uses_lsget_in_init():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    # assembledOnly init should use lsGet
    idx = src.index("assembledOnly, setAssembledOnly")
    snippet = src[idx : idx + 80]
    assert "lsGet" in snippet, "assembledOnly not initialized from lsGet"


def test_typescript_compiles():
    import subprocess
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd="admin/wms_admin_frontend",
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
