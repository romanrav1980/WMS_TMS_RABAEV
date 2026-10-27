from api.wms_api_server.app.modules.inventory.infrastructure.case_pick_policy import case_pick_policy


class PolicyGateway:
    def __init__(self, *, weighted, serialized, marking):
        self.weighted = weighted
        self.serialized = serialized
        self.marking = marking

    def fetch_all(self, sql, params):
        if "from RRL_CASE_PICK_LINE" in sql:
            return [{"articul": "SKU-1", "weighted_kg": self.weighted,
                     "serialized_weight_boxes": self.serialized, "marking_required": self.marking}]
        return [{"system_code": "CRPT", "profile_code": "UNIT"}] if self.marking else []


def test_marked_weighted_kg_line_is_distinct_from_loose_weight_eligibility():
    result = case_pick_policy(PolicyGateway(weighted=1, serialized=0, marking=1), 11, 22)

    assert result["weighted_kg"] is True
    assert result["loose_weight_kg"] is False
    assert result["marking_required"] is True
    assert result["profiles"] == [{"system_code": "CRPT", "profile_code": "UNIT"}]


def test_serialized_weight_boxes_are_not_manual_net_kg_lines():
    result = case_pick_policy(PolicyGateway(weighted=1, serialized=1, marking=0), 11, 22)

    assert result["weighted_kg"] is False
    assert result["loose_weight_kg"] is False
