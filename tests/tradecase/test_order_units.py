"""C-0175: the order-unit normalizer (owner rule 27.10.2026) on registry-shaped coefficients; no database. KG cases check the pure
fractional-step arithmetic only; weighed base-KG orders end-to-end are not part of this first stage."""
from decimal import Decimal
from app.modules.integrations.domain.order_units import Conversion, normalize_line

EA = Conversion(1, 1, "EA", 0, 3)
BOX12 = Conversion(12, 1, "EA", 0, 4)
BLK10 = Conversion(10, 1, "EA", 0, 2)
KG = Conversion(1, 1, "KG", 3, 5)
G = Conversion(1, 1000, "KG", 3, 5)
PIECES = dict(EA=EA, BOX=BOX12, BLK=BLK10)
ONE = Decimal(1)


def test_25_and_24_pieces_box_12_are_2_boxes_in_both_modes():
    for qty, base, diff, status in ((25, "25", "1", "ROUNDED_DOWN"), (24, "24", "0", "CONVERTED")):
        allowed = normalize_line(Decimal(qty), "EA", "BOX", ONE, True, PIECES)
        forbidden = normalize_line(Decimal(qty), "EA", "BOX", ONE, False, PIECES)
        for r in (allowed, forbidden):
            assert (r["quantity"], r["uom"], r["base_quantity"], r["processed_base_quantity"], r["base_difference"], r["status"]) == ("2", "BOX", base, "24", diff, status)
            assert (r["source_quantity"], r["source_uom"], r["executable"]) == (str(qty), "EA", True)
        assert (allowed["error_code"], allowed["integration_error"]) == (None, False)
        # Flag off and another source unit: loaded with the integration error, even for the exact 24 pieces.
        assert (forbidden["error_code"], forbidden["integration_error"]) == ("ORDER_UNIT_ROUNDING_NOT_ALLOWED", True)
    assert normalize_line(Decimal(25), "EA", "BOX", ONE, True, PIECES)["conversion_policy"] == {"BOX": 4, "EA": 3}


def test_never_rounds_up_and_the_processing_unit_itself_has_no_error():
    assert normalize_line(Decimal(35), "EA", "BOX", ONE, True, PIECES)["quantity"] == "2"  # not 3
    same = normalize_line(Decimal(3), "BOX", "BOX", ONE, False, PIECES)
    assert (same["quantity"], same["status"], same["base_difference"], same["integration_error"]) == ("3", "EXACT", "0", False)
    stepped = normalize_line(Decimal(50), "EA", "BOX", Decimal(2), True, PIECES)  # step of 2 boxes: 50 pieces -> 4 boxes (48)
    assert (stepped["quantity"], stepped["base_difference"]) == ("4", "2")


def test_blocks_with_explicit_code_mapping_keep_the_source_code():
    for code in ("BLOCK", "BLK"):
        r = normalize_line(Decimal(5), code, "BOX", ONE, True, PIECES)  # 50 pieces -> 4 boxes (48), 2 left
        assert (r["quantity"], r["base_difference"], r["status"], r["source_uom"]) == ("4", "2", "ROUNDED_DOWN", code)
    assert normalize_line(Decimal("2.5"), "BLK", "EA", ONE, True, PIECES)["quantity"] == "25"


def test_fractional_step_arithmetic():
    kg = dict(KG=KG, G=G)
    r = normalize_line(Decimal(1250), "G", "KG", Decimal("0.001"), True, kg)
    assert (r["quantity"], r["status"]) == ("1.25", "CONVERTED")  # 1.25 kg, not 1 kg
    fine = normalize_line(Decimal("1250.4"), "G", "KG", Decimal("0.001"), True, kg)
    assert (fine["quantity"], fine["base_difference"], fine["status"]) == ("1.25", "0.0004", "ROUNDED_DOWN")
    quarter = normalize_line(Decimal(1300), "G", "KG", Decimal("0.25"), True, kg)  # another fractional step
    assert (quarter["quantity"], quarter["base_difference"]) == ("1.25", "0.05")


def test_zero_missing_setting_and_coefficient_keep_the_line_non_executable():
    zero = normalize_line(Decimal(11), "EA", "BOX", ONE, True, PIECES)
    assert (zero["quantity"], zero["status"], zero["executable"], zero["error_code"], zero["base_difference"]) == ("0", "ZERO", False, "ORDER_LINE_ZERO_AFTER_ROUNDING", "11")
    missing = normalize_line(Decimal(3), "BLOCK", "BOX", ONE, True, dict(EA=EA, BOX=BOX12))
    assert (missing["quantity"], missing["status"], missing["executable"], missing["error_code"]) == (None, "COEFFICIENT_MISSING", False, "ORDER_UNIT_COEFFICIENT_MISSING:BLK")
    assert normalize_line(Decimal(3), "EA", "BOX", None, True, PIECES)["status"] == "PROCESSING_STEP_REQUIRED"
    legacy = normalize_line(Decimal(25), "EA", None, None, False, {})
    assert (legacy["quantity"], legacy["uom"], legacy["status"], legacy["integration_error"]) == ("25", "EA", "UNCHANGED", False)
    assert normalize_line(Decimal(1), "KG", None, None, True, {})["status"] == "PROCESSING_UNIT_REQUIRED"
    assert normalize_line(Decimal(1), "KG", "BOX", ONE, True, dict(KG=KG, BOX=BOX12))["error_code"] == "ORDER_UNIT_BASE_MISMATCH"


# --- intake glue and the NOT_APPLIED native kit ---------------------------------------------------------------------------------
import hashlib
import json
import pathlib
from app.modules.integrations.infrastructure.tradecase_documents import OracleTradecaseDocuments

KIT = pathlib.Path(__file__).resolve().parents[2] / "db/migrations/2026-10-27_trade_order_units"


class Cur:
    def __init__(self, stored=None, sku=None, registry=()):
        self.stored, self.sku, self.registry, self.rows, self.sql = stored, sku, list(registry), [], []

    def execute(self, sql, **kw):
        self.sql.append(sql)
        if "RRL_TRADE_MESSAGE" in sql:
            self.rows = [self.stored] if self.stored else []
        elif "RRL_TRADE_DOCUMENT" in sql:
            self.rows = [self.sku] if self.sku else []
        elif "RRL_STOCK_UOM_CONVERSION" in sql:
            self.rows = self.registry

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows


def order(lines, kind="OUTBOUND"):
    return dict(warehouse_id=1, source_id="SAP", event_id="E1", payload_hash="h1",
                payload=dict(entity_type="ORDER", order_kind=kind, lines=[dict(line_id=str(i), sku_id="A", quantity=q, uom=u) for i, (q, u) in enumerate(lines, 1)]))


SKU = (json.dumps(dict(wms_article_id="ART", units_per_box=12, processing_uom="BOX", processing_step="1", round_to_processing_unit=False)), 7)
REGISTRY = [("EA", 1, 1, "EA", 0, 3), ("BOX", 12, 1, "EA", 0, 4)]


def test_intake_normalizes_from_the_current_sku_and_registry():
    value = OracleTradecaseDocuments(None)._normalize_order(Cur(sku=SKU, registry=REGISTRY), order([("25", "EA")]))
    line = value["payload"]["lines"][0]
    assert (line["quantity"], line["uom"]) == ("2", "BOX")
    assert line["normalization"]["error_code"] == "ORDER_UNIT_ROUNDING_NOT_ALLOWED" and line["normalization"]["sku_version"] == 7


def test_exact_replay_uses_the_stored_request_without_renormalizing():
    stored_request = order([("2", "BOX")]); stored_request["payload"]["lines"][0]["normalization"] = {"status": "STORED"}
    cur = Cur(stored=("h1", json.dumps(stored_request)), sku=SKU, registry=REGISTRY)
    assert OracleTradecaseDocuments(None)._normalize_order(cur, order([("25", "EA")])) == stored_request
    assert not any("RRL_STOCK_UOM_CONVERSION" in q for q in cur.sql)


def test_buyout_and_unconfigured_sku_keep_the_current_contract():
    buyout = order([("25", "EA")], "BUYOUT")
    assert OracleTradecaseDocuments(None)._normalize_order(Cur(sku=SKU, registry=REGISTRY), buyout)["payload"]["lines"][0]["quantity"] == "25"
    plain = (json.dumps(dict(wms_article_id="ART", units_per_box=12)), 1)
    line = OracleTradecaseDocuments(None)._normalize_order(Cur(sku=plain), order([("25", "EA")]))["payload"]["lines"][0]
    assert (line["quantity"], line["uom"], "normalization" in line) == ("25", "EA", False)
    missing = OracleTradecaseDocuments(None)._normalize_order(Cur(), order([("5", "BLK")]))["payload"]["lines"][0]
    assert (missing["quantity"], missing["normalization"]["status"], missing["normalization"]["executable"]) == ("0", "SKU_SETTINGS_MISSING", False)


def test_native_kit_hashes_and_edits():
    m = json.loads((KIT / "manifest.json").read_text(encoding="utf-8"))
    assert m["status"] == "NOT_APPLIED" and not m["applied_by_claude"]
    for name, sha in m["files_sha256"].items():
        assert hashlib.sha256((KIT / name).read_bytes()).hexdigest() == sha, name
    doc = (KIT / "001_document_api_body.sql").read_text(encoding="utf-8")
    assert "NON_EXECUTABLE_LINE_QUANTITY_MUST_BE_ZERO" in doc and "ORDER_LINE_NOT_EXECUTABLE" in doc and doc.count("function inert") == 1
    bind = (KIT / "002_order_api_body.sql").read_text(encoding="utf-8")
    assert "continue when inert(line);" in bind and "if n<>v_exec or n<>maps.get_size" in bind
    rollback = (KIT / "rollback.sql").read_text(encoding="utf-8")
    assert rollback.index("AFTER_SOURCE_DRIFT_REFUSED") < rollback.index("TRADE_ORDER_UNIT_HISTORY_PRESENT") < rollback.index("@@before_document_api_body.sql")
