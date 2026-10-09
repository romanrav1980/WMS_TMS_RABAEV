import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"api/wms_api_server"))
import pytest
from app.modules.inventory.domain.carrier_shipment import assert_matching_composition


def test_multiple_lots_match_boxes_in_exact_base_units():
    assert_matching_composition([("A","EA","4.5"),("A","EA","7.5"),("B","KG","0.125")],
        [("A","1","EA",12,1,9),("B","125","KG",1,1000,9)])


def test_large_quantity_preserves_last_decimal_without_rounding():
    assert_matching_composition([("A","EA","9007199254740993.000000001")],
        [("A","9007199254740993.000000001","EA",1,1,9)])


@pytest.mark.parametrize("physical,document",[
    ([("A","EA","2")],[("A","1","EA",1,1,9)]),
    ([("A","EA","1"),("B","EA","1")],[("A","1","EA",1,1,9)]),
    ([("A","EA","1")],[("B","1","EA",1,1,9)]),
    ([("A","KG","1")],[("A","1","EA",1,1,9)]),
    ([("A","EA","1")],[("A","1","EA",None,None,None)]),
    ([("A","EA","1")],[("A","1","EA",1,3,9)]),
    ([],[("A","1","EA",1,1,9)]),
])
def test_incomplete_foreign_unit_or_rounding_composition_rejected(physical,document):
    with pytest.raises(ValueError):
        assert_matching_composition(physical,document)
