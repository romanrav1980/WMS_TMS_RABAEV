"""Sprint 68: Ctrl+Enter keyboard shortcut to add selected STs to trip."""
import pytest


def test_ctrl_enter_handler_present():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert 'e.ctrlKey || e.metaKey' in src, "Ctrl/Cmd modifier not detected"
    assert 'handleAssign' in src[src.index("Sprint 68"):src.index("Sprint 68") + 500], \
        "handleAssign not called from Sprint 68 block"


def test_button_tooltip_ctrl_enter():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    assert 'title="Ctrl+Enter"' in src, "Ctrl+Enter tooltip not on assign button(s)"


def test_effect_deps_include_active_tab():
    src = open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()
    # The keydown useEffect closure must reference activeTab
    idx = src.index("Sprint 44")
    snippet = src[idx : idx + 1500]
    assert "activeTab" in snippet, "activeTab not in keydown effect deps"


def test_typescript_compiles():
    import subprocess
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd="admin/wms_admin_frontend",
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
