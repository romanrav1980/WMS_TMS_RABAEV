"""C-0148 offline checks of route point -> TRADECASE recipient links (keys only) with a scripted cursor (no Oracle)."""
import json
import pytest
from app.modules.integrations.contracts_trade_transport import TradeTransportError
from app.modules.integrations.infrastructure.trade_route_plan import route_points

POINTS = [(1, "ST1", 7, "ADDR-1", 1, None, None), (2, "ST2", 7, "ADDR-2", 2, "2026-11-02T11:00:00", "2026-11-02T11:15:00"),
          (3, "ST3", 7, "ADDR-3", 3, None, None), (4, "ST4", 7, "ADDR-4", 4, None, None), (5, "ST5", 9, "FOREIGN", 5, None, None),
          (6, "ST6", 7, None, 6, None, None)]
ORDERS = {1: [(101, 501, "O1", "R1", 7)], 2: [], 3: [(103, 503, "O3", "R3", 7), (104, 504, "O4", "R4", 7)], 4: [(105, 505, "OH", "RH", 7)],
          6: [(106, 501, "O6", "R1", 7)]}
OWNERS = {"O1": ["SNS"], "O3": ["SNS"], "O4": ["SNS"], "OH": ["HIDDEN"], "O6": ["SNS"]}
RECIPIENTS = {"R1": {"title": "Филиал", "wms_customer_id": 501}}
ADDRESSES = {(501, "ADDR-1"): ["STORE"]}


class Cur:
    def __init__(self, linked=True, trip=True, allowed=True, points=None):
        self.linked, self.trip, self.allowed, self.rows, self.sql = linked, trip, allowed, [], []
        self.points = points if points is not None else [p for p in POINTS if p[0] not in (4,5)]

    def execute(self, sql, **kw):
        s = " ".join(sql.split()); self.sql.append(s)
        if s.startswith("set transaction"): self.rows = []
        elif "RRL_ACCESS_API.allowed" in s: self.rows = [(1 if self.allowed else 0,)]
        elif "ENTITY_TYPE='TRIP'" in s: self.rows = [(1 if self.trip else 0,)]
        elif "from RRL_TRADE_TRIP_LINK" in s: self.rows = [(33660,)] if self.linked else []
        elif "from RRL_SBORKA_PALLETS sp where sp.TRANSTASK_ID" in s: self.rows = self.points
        elif "select distinct o.CUSTOMER_ORDER_ID" in s: self.rows = ORDERS[kw["sp"]]
        elif "ol.SOURCE_OWNER_ID from RRL_TRADE_ORDER_LINK" in s: self.rows = [(o,) for o in OWNERS[kw["o"]]]
        elif "owner_allowed" in s: self.rows = [(0 if kw["o"] == "HIDDEN" else 1,)]
        elif "ENTITY_TYPE='RECIPIENT'" in s:
            body = RECIPIENTS.get(kw["r"]); self.rows = [] if body is None else [(json.dumps(body),)]
        elif "from RRL_CUSTOMER_ADDRESS" in s: self.rows = [(t,) for t in ADDRESSES.get((kw["c"], kw["a"]), [])]
        else: raise AssertionError(s)

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows


class Gateway:
    def __init__(self, cur): self.cur = cur

    def transaction(self, name):
        cur = self.cur

        class Ctx:
            def __enter__(self): return cur
            def __exit__(self, *a): return False
        return Ctx()


def test_links_only_by_keys_and_hides_what_must_be_hidden():
    cur = Cur()
    r = route_points(Gateway(cur), 7, "R1", "u")
    assert "set transaction read only" in cur.sql[0]
    by = {p["point_id"]: p for p in r["points"]}
    assert by[1]["link_status"] == "LINKED" and by[1]["recipient_id"] == "R1" and by[1]["customer_consistent"] is True
    assert by[1]["address_status"] == "CONFIRMED" and by[1]["address_type"] == "STORE"
    assert by[2] == {**by[2], "link_status": "UNLINKED", "reason": "NO_ORDER_FOR_POINT"}
    assert by[3]["link_status"] == "AMBIGUOUS" and "recipient_id" not in by[3]
    assert 4 not in by and 5 not in by
    assert by[6]["link_status"] == "LINKED" and by[6]["address_status"] == "ADDRESS_MISSING"
    assert r["blocked_reason"] == "POINT_RECIPIENT_LINK_INCOMPLETE" and r["route_executed"] is False
    assert not any("RECIPIENT" in s and "title" in s for s in cur.sql)  # no name-based lookup anywhere


@pytest.mark.parametrize('point_id',[4,5])
def test_hidden_or_foreign_stop_hides_entire_route_without_identifiers_or_counts(point_id):
    cur=Cur(points=[p for p in POINTS if p[0] in (1,point_id)])
    result=route_points(Gateway(cur),7,'R1','u')
    assert result['points']==[] and result['blocked_reason']=='ROUTE_POINTS_NOT_VISIBLE'
    text=json.dumps(result)
    assert not any(secret in text for secret in ('ADDR-','ST1','ST4','ST5','FOREIGN','recipient_id'))


def test_mixed_hidden_owner_does_not_disclose_recipient_ambiguity():
    old=OWNERS['O4']
    OWNERS['O4']=['HIDDEN']
    try:
        result=route_points(Gateway(Cur()),7,'R1','u')
        assert result['points']==[] and result['blocked_reason']=='ROUTE_POINTS_NOT_VISIBLE'
        assert 'SEVERAL_RECIPIENTS' not in json.dumps(result)
    finally:
        OWNERS['O4']=old


def test_recipient_without_customer_and_mismatched_customer():
    RECIPIENTS["R3X"] = {"title": "Без клиента"}
    ORDERS[1] = [(101, 999, "O1", "R1", 7)]
    try:
        r = route_points(Gateway(Cur()), 7, "R1", "u")
        p = next(x for x in r["points"] if x["point_id"] == 1)
        assert p["customer_consistent"] is False and p["address_status"] == "NOT_IN_CUSTOMER_ADDRESSES"
    finally:
        ORDERS[1] = [(101, 501, "O1", "R1", 7)]


def test_unbound_trip_is_explicit_and_unknown_trip_is_404_and_denied_is_403():
    r = route_points(Gateway(Cur(linked=False)), 7, "R1", "u")
    assert r["points"] == [] and r["blocked_reason"] == "TRIP_NOT_BOUND" and r["native_task_id"] is None
    with pytest.raises(TradeTransportError) as missing:
        route_points(Gateway(Cur(trip=False)), 7, "NOPE", "u")
    assert missing.value.status == 404
    with pytest.raises(TradeTransportError) as denied:
        route_points(Gateway(Cur(allowed=False)), 7, "R1", "u")
    assert denied.value.status == 403
