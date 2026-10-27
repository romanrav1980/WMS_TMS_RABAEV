"""Review regressions: mixed receipts, concurrent-winner readback and exact decimals."""
from contextlib import contextmanager
from decimal import Decimal, localcontext
from fractions import Fraction
import json

import pytest
from pydantic import ValidationError
from app.modules.integrations.domain.order_units import Conversion, _text, normalize_line
from app.modules.integrations.infrastructure.tradecase_documents import OracleTradecaseDocuments
from app.modules.integrations.contracts_tradecase import TradeSku


class NativeValue:
    def __init__(self):
        self.value = None
    def setvalue(self, position, value):
        self.value = value
    def getvalue(self):
        return self.value


class ReceiptCursor:
    def __init__(self, persisted):
        self.persisted = persisted
        self.reads = []
    def var(self, *args):
        return NativeValue()
    def callproc(self, procedure, args):
        args[-1].setvalue(0, json.dumps(dict(status='ACCEPTED', event_id='E1')))
    def execute(self, sql, **binds):
        self.reads.append((sql, binds))
    def fetchone(self):
        return (json.dumps(self.persisted),)


class ReceiptGateway:
    def __init__(self, persisted):
        self.cursor = ReceiptCursor(persisted)
    @contextmanager
    def transaction(self, *args):
        yield self.cursor


def test_receipt_uses_persisted_winner_and_includes_unchanged_lines():
    outcome = dict(status='ROUNDED_DOWN', error_code=None, integration_error=False, executable=True)
    winner = dict(source_id='SAP', event_id='E1', payload=dict(entity_type='ORDER', lines=[
        dict(line_id='1', quantity='2', uom='BOX', normalization=outcome),
        dict(line_id='2', quantity='3', uom='BOX')]))
    losing_attempt = json.loads(json.dumps(winner))
    losing_attempt['payload']['lines'][0]['quantity'] = '99'
    gateway = ReceiptGateway(winner)
    result = OracleTradecaseDocuments(gateway)._command('receive_document', 42, 'admin', losing_attempt)
    assert [x['quantity'] for x in result['line_results']] == ['2', '3']
    assert result['line_results'][1]['status'] == 'UNCHANGED'
    assert result['loaded_with_integration_error'] is False
    assert gateway.cursor.reads[0][1] == dict(w=42, s='SAP', e='E1')


def test_decimal_text_is_exact_independently_of_decimal_context():
    with localcontext() as context:
        context.prec = 6
        text = _text(Fraction(1, 2**128))
        source = normalize_line(Decimal('123456789012.123456'), 'EA', None, None, True, {})
    assert Fraction(Decimal(text)) == Fraction(1, 2**128)
    assert source['source_quantity'] == '123456789012.123456'
    with pytest.raises(ValueError):
        _text(Fraction(1, 3))


def test_recurring_coefficient_keeps_raw_line_without_a_rounded_decimal():
    result = normalize_line(Decimal('1'), 'G', 'EA', Decimal('1'), True,
        dict(G=Conversion(1, 3, 'EA', 0, 1), EA=Conversion(1, 1, 'EA', 0, 1)))
    assert (result['quantity'], result['executable'], result['source_quantity']) == (None, False, '1')
    assert result['error_code'] == 'ORDER_UNIT_EXACT_DECIMAL_REQUIRED'


def test_tradecase_discrete_processing_setting_refuses_a_fractional_box_step():
    with pytest.raises(ValidationError):
        TradeSku(entity_type='SKU', title='Review fixture', units_per_box=12, permitted_mrc=['1'],
                 processing_uom='BOX', processing_step='0.5', round_to_processing_unit=True)
