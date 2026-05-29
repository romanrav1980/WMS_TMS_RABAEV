"""Sprint 81: ↑/↓ keyboard navigation between trips."""
import pytest


def _src():
    return open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()


def test_data_taskid_attribute_in_tasks_tab():
    src = _src()
    idx = src.index("sortedTasks.map(task =>")
    snippet = src[idx : idx + 300]
    assert "data-taskid={task.ID}" in snippet, "data-taskid missing in tasks tab rows"


def test_data_taskid_attribute_in_routes_tab():
    src = _src()
    idx = src.index("searchedRouteTasks.map(task =>")
    snippet = src[idx : idx + 300]
    assert "data-taskid={task.ID}" in snippet, "data-taskid missing in routes tab rows"


def test_arrow_key_handler_present():
    src = _src()
    assert "ArrowUp" in src, "ArrowUp handler missing"
    assert "ArrowDown" in src, "ArrowDown handler missing"


def test_navigate_wraps_around():
    src = _src()
    assert "list[0]" in src, "Wrap-to-first missing in ArrowDown branch"
    assert "list[list.length - 1]" in src, "Wrap-to-last missing in ArrowUp branch"


def test_scroll_into_view_effect():
    src = _src()
    assert "scrollIntoView" in src, "scrollIntoView call missing"
    assert 'data-taskid="${selectedTask.ID}"' in src or "data-taskid" in src


def test_typescript_compiles():
    from tests.support.frontend_checks import run_tsc_no_emit
    r = run_tsc_no_emit()
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"
