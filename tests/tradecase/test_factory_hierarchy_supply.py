"""C-0168 offline checks: a factory pallet (SSCC) listing its boxes in the supplier composition of the existing supply order; one SSCC
scan expands every box through the existing ReceivingMarks; the hierarchy refusals. Live receipt: tests/tradecase/live_factory_hierarchy.py."""
from decimal import Decimal
import json
import xml.etree.ElementTree as ET
import pytest
from app.modules.integrations.domain.supply_order import read_supply_order
from app.modules.inventory.infrastructure.receiving_marks import ReceivingMarks

GTIN = "29023099475271"


def code(n):
    return GTIN + "abc" + str(n).zfill(4)


def order(boxes=((1, 6), (7, 4)), pallet_children=("B1", "B2"), pallet_units=(), extra=None, child_level="BOX", second_pallet=None):
    root = ET.Element("WarehouseSupplyOrder", version="1")
    for k, v in dict(Sender="TC03.QA.SAP", MessageId="M1", OrderNumber="F1", Revision="1", WarehouseId="210000001", ReceiveCell="R1", Supplier="Factory").items():
        ET.SubElement(root, k).text = v
    line = ET.SubElement(ET.SubElement(root, "Lines"), "Line")
    ET.SubElement(line, "LineNumber").text = "1"; ET.SubElement(line, "Material").text = "TC03X"
    ET.SubElement(line, "Quantity", unit="EA").text = "10"
    aggs = ET.SubElement(root, "Aggregations")

    def agg(level, agg_code, units, children=None):
        a = ET.SubElement(aggs, "Aggregation")
        for k, v in dict(LineNumber="1", System="CRPT", Profile="TOBACCO", Level=level, Code=agg_code).items():
            ET.SubElement(a, k).text = v
        if children is not None:
            c = ET.SubElement(a, "Children")
            for ch in children:
                ET.SubElement(ET.SubElement(c, "Child"), "Code").text = ch
        if units:
            u = ET.SubElement(a, "Units")
            for n in units:
                m = ET.SubElement(u, "Unit"); ET.SubElement(m, "UnitId").text = str(n); ET.SubElement(m, "Quantity").text = "1"
                ET.SubElement(m, "Code").text = code(n)
    for i, (start, size) in enumerate(boxes, 1):
        agg(child_level, "B" + str(i), range(start, start + size))
    agg("PALLET", "SSCC1", pallet_units, list(pallet_children))
    if second_pallet:
        agg("PALLET", "SSCC2", (), list(second_pallet))
    if extra:
        extra(agg)
    return ET.tostring(root)


def test_factory_pallet_expands_its_boxes_and_keeps_the_boxes():
    parsed = read_supply_order(order())
    by_code = {a["code"]: a for a in parsed["aggregations"]}
    assert [u["unit_id"] for u in by_code["SSCC1"]["units"]] == [str(n) for n in range(1, 11)]
    assert len(by_code["B1"]["units"]) == 6 and len(by_code["B2"]["units"]) == 4  # boxes stay scannable on their own
    assert by_code["SSCC1"]["level"] == "PALLET" and by_code["B1"]["level"] == "BOX"
    # a pallet may also carry loose units next to its boxes
    mixed = {a["code"]: a for a in read_supply_order(order(boxes=((1, 6),), pallet_children=("B1",), pallet_units=range(7, 11)))["aggregations"]}
    assert len(mixed["SSCC1"]["units"]) == 10


@pytest.mark.parametrize("kwargs,message", [
    (dict(pallet_children=("B1", "B9")), "same line and profile"),          # unknown child
    (dict(child_level="PALLET"), "same line and profile"),                  # child is not a box
    (dict(pallet_children=("B1", "B1")), "one factory pallet"),             # the same box twice
    (dict(second_pallet=("B1",)), "one factory pallet"),                    # a box in two pallets
    (dict(boxes=((1, 6), (6, 4))), "overlap"),                              # boxes share a unit
    (dict(pallet_children=()), "1..1000 child boxes"),                      # empty children
])
def test_wrong_hierarchy_is_refused(kwargs, message):
    with pytest.raises(ValueError, match=message):
        read_supply_order(order(**kwargs))


def test_only_a_pallet_lists_children_and_flat_messages_are_unchanged():
    def box_with_children(agg):
        agg("BOX", "B3", range(20, 22), ["B1"])
    with pytest.raises(ValueError, match="Only a PALLET"):
        read_supply_order(order(extra=box_with_children))
    flat = read_supply_order(order(pallet_children=("B1",), boxes=((1, 6),)).replace(b"<Children><Child><Code>B1</Code></Child></Children>", b"<Units><Unit><UnitId>99</UnitId><Code>" + code(99).encode() + b"</Code></Unit></Units>"))
    assert {a["code"]: len(a["units"]) for a in flat["aggregations"]} == {"B1": 6, "SSCC1": 1}


class Cur:
    """ReceivingMarks against the composition stored per node, as supply_orders.py writes it into RRL_SAP_TRACE_AGG."""

    def __init__(self, stored, mode):
        self.stored, self.mode, self.rows = stored, mode, []

    def execute(self, sql, params=None, **kw):
        p = {**(params or {}), **kw}
        if "RRL_SKU_RECEIPT_POLICY" in sql:
            self.rows = [(3, 1, 0)]
        elif "RRL_SKU_RECEIPT_PROFILE" in sql:
            self.rows = [("CRPT", "TOBACCO", "TC03.F", self.mode)]
        elif "RRL_SAP_TRACE_AGG" in sql:
            hit = self.stored.get((p["code_hash"], p["agg_level"]))
            self.rows = [(json.dumps(hit),)] if hit else []

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows


def stored_nodes():
    from hashlib import sha256
    return {(sha256(a["code"].encode()).hexdigest(), a["level"]): a["units"] for a in read_supply_order(order())["aggregations"]}


def scan(level, agg_code):
    return {"system_code": "CRPT", "profile_code": "TOBACCO", "level": level, "code": agg_code}


def test_one_sscc_scan_receives_the_whole_factory_pallet(monkeypatch):
    monkeypatch.setattr("app.modules.inventory.infrastructure.receiving_marks.assert_capture_policy", lambda *a: None)
    marks = ReceivingMarks(Cur(stored_nodes(), "PALLET")).resolve("O1", "TC03X", "1", Decimal(10), {"units": [], "aggregations": [scan("PALLET", "SSCC1")]}, "EA")
    assert len(marks["units"]) == 10 and marks["scanned"] == [{"system": "CRPT", "profile": "TOBACCO", "version": "TC03.F", "level": "PALLET", "code": "SSCC1"}]
    boxes = ReceivingMarks(Cur(stored_nodes(), "BOX")).resolve("O1", "TC03X", "1", Decimal(10), {"units": [], "aggregations": [scan("BOX", "B1"), scan("BOX", "B2")]}, "EA")
    assert len(boxes["units"]) == 10  # box by box still works under a BOX profile


def test_receipt_refusals(monkeypatch):
    monkeypatch.setattr("app.modules.inventory.infrastructure.receiving_marks.assert_capture_policy", lambda *a: None)
    rm = lambda mode: ReceivingMarks(Cur(stored_nodes(), mode))
    with pytest.raises(ValueError, match="more than once"):  # the pallet and one of its boxes in one receipt
        rm("UNIT_OR_AGGREGATION").resolve("O1", "TC03X", "1", Decimal(10), {"units": [], "aggregations": [scan("PALLET", "SSCC1"), scan("BOX", "B1")]}, "EA")
    with pytest.raises(ValueError, match="forbidden by WMS receiving profile"):  # SSCC scan under a BOX-only profile
        rm("BOX").resolve("O1", "TC03X", "1", Decimal(10), {"units": [], "aggregations": [scan("PALLET", "SSCC1")]}, "EA")
    with pytest.raises(ValueError, match="Unknown aggregation composition"):
        rm("PALLET").resolve("O1", "TC03X", "1", Decimal(10), {"units": [], "aggregations": [scan("PALLET", "SSCC-UNKNOWN")]}, "EA")
    with pytest.raises(ValueError, match="must equal pallet quantity"):
        rm("PALLET").resolve("O1", "TC03X", "1", Decimal(9), {"units": [], "aggregations": [scan("PALLET", "SSCC1")]}, "EA")
