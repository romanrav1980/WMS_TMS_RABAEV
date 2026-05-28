"""Sprint 82: Fix dispatch-st-ready condition + persist stDate and dateTo."""


def _src():
    return open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()


def test_dispatch_st_ready_uses_100_not_1():
    src = _src()
    assert "st.VERIFY_PERC === 1.0" not in src, "Old buggy condition still present"
    assert ">= 100" in src, "Fixed condition >= 100 missing"


def test_stdate_uses_own_localstorage_key():
    src = _src()
    assert 'lsGet("tms_stDate"' in src, "stDate should read from tms_stDate, not tms_filterDate"


def test_dateto_persisted_to_localstorage():
    src = _src()
    assert '"tms_dateTo"' in src, "tms_dateTo localStorage key missing"
    idx = src.index("tms_dateTo")
    snippet = src[max(0, idx - 100) : idx + 200]
    assert "dateTo" in snippet


def test_stdate_persistence_effect():
    src = _src()
    assert 'localStorage.setItem("tms_stDate"' in src


def test_dateto_persistence_effect():
    src = _src()
    assert 'localStorage.setItem("tms_dateTo"' in src


def test_dateto_init_from_localstorage():
    src = _src()
    assert 'useState<string>(() => lsGet("tms_dateTo"' in src
