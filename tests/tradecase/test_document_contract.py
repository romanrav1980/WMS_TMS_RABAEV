from copy import deepcopy

import pytest
from pydantic import ValidationError

from api.wms_api_server.app.modules.integrations.contracts_tradecase import TradeEnvelope
from api.wms_api_server.app.modules.integrations.infrastructure.tradecase_documents import canonical


def order():
    return dict(schema_version=1, event_id="e1", source_id="SAP", warehouse_id=1,
                document_id="O1", version=1, occurred_at="2026-10-19T09:00:00+03:00",
                payload=dict(entity_type="ORDER", recipient_id="C1", planned_ship_at="2026-10-19T10:00:00+03:00",
                             lines=[dict(line_id="10", sku_id="A", source_owner_id="SNS", target_owner_id="BLC",
                                         mrc="200.00", quantity="25", uom="BOX", min_osg_days=50)]))


def test_rejects_naive_external_times():
    for path in ("occurred_at", "planned_ship_at"):
        body = order()
        target = body if path == "occurred_at" else body["payload"]
        target[path] = "2026-10-19T10:00:00"
        with pytest.raises(ValidationError):
            TradeEnvelope.model_validate(body)


@pytest.mark.parametrize("field,value", [("quantity", "NaN"), ("quantity", "0"), ("quantity", "-1"), ("mrc", "200.001")])
def test_rejects_invalid_quantities_and_prices(field, value):
    body = order()
    body["payload"]["lines"][0][field] = value
    with pytest.raises(ValidationError):
        TradeEnvelope.model_validate(body)


def test_business_numbers_canonicalize_without_float_loss():
    first = order()
    second = deepcopy(first)
    second["payload"]["lines"][0].update(mrc="200", quantity="25.000")
    assert canonical(TradeEnvelope.model_validate(first).model_dump(mode="json")) == canonical(TradeEnvelope.model_validate(second).model_dump(mode="json"))


def test_duplicate_lines_cannot_hide_extra_assignment():
    body = order()
    body["payload"]["lines"].append(deepcopy(body["payload"]["lines"][0]))
    with pytest.raises(ValidationError, match="Duplicate order line"):
        TradeEnvelope.model_validate(body)


def test_topup_requires_explicit_parent_trip():
    body = order()
    body["payload"]["order_kind"] = "TOPUP"
    with pytest.raises(ValidationError, match="parent trip"):
        TradeEnvelope.model_validate(body)


def test_unknown_fields_cannot_enable_unapproved_profile():
    body = order()
    body["payload"]["force_release"] = True
    with pytest.raises(ValidationError):
        TradeEnvelope.model_validate(body)
