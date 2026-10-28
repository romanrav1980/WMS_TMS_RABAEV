from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "db" / "migrations" / "2026-10-28_multi_order_root_hu_shipping"


def read(name: str) -> str:
    return (MIGRATION / name).read_text(encoding="utf-8")


def test_multi_order_shipment_stays_inside_existing_shipping_core():
    core = read("002_shipping_core.sql")
    assert "procedure compile_multi_order_shipment" in core
    assert "procedure execute_multi_order_resolved" in core
    assert "RRL_STOCK_MULTI_ORDER_SHIP" not in core
    assert "compile_multi_order_shipment(p_request,p_operation,p_policies,p_resources,p_domain,p_skip_qc);return;" in core
    assert "execute_multi_order_resolved(p_request,p_domain,p_offset,p_actor,p_result);return;" in core


def test_multi_order_execution_requires_one_root_hu_operation():
    core = read("002_shipping_core.sql")
    assert "if v_root_kind!='HU_SHIP' then raise_application_error(-20886,'SHIPMENT_WHOLE_HU_REQUIRED');end if;" in core
    assert "RRL_STOCK_QC_GATE.assert_approved(p_domain);" in core
    assert "RRL_QC_SCOPE_READ.record_exemption(p_domain,RRL_STOCK_QC_GATE.signature_for_plan(p_domain));" in core


def test_migration_does_not_expand_access_to_protected_stock_cores():
    assert "RRL_STOCK_MULTI_ORDER_SHIP" not in read("001_multi_order_ship_contract.sql")
    assert "RRL_STOCK_MULTI_ORDER_SHIP" not in read("apply.sql")
    assert "RRL_STOCK_MULTI_ORDER_SHIP" not in read("rollback.sql")
    assert "RRL_STOCK_MULTI_ORDER_SHIP" not in read("verify.sql")
    assert "RRL_STOCK_MULTI_ORDER_SHIP" not in read("rollback_verify.sql")
