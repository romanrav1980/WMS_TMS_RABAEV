"""Carton-trip read windows: preserve every fact or refuse the whole response."""
import json
from decimal import Decimal

import pytest
from app.modules.transport.infrastructure import loading_status as status_module
from app.modules.transport.infrastructure.loading_floor_read import loading_floor_read
from app.modules.transport.infrastructure.loading_thermal_read import loading_thermal_read
from app.modules.transport.contracts import TransportLoadingError
from app.modules.integrations.contracts_trade_transport import TradeTransportError
from app.modules.integrations.infrastructure.trade_capacity import _loaded


class Cursor:
    def __init__(self, members=(), loads=(), floor=(), thermal=()):
        self.members, self.loads, self.floor, self.thermal = members, loads, floor, thermal
        self.rows, self.calls = [], []

    def execute(self, sql, **binds):
        self.calls.append((sql, binds))
        if 'from RRL_SBORKA_PALLETS sp left join' in sql:
            self.rows = self.members
        elif 'from RRL_TT_HU_LOAD_FACT where TT_ID=' in sql:
            self.rows = self.loads
        elif 'from RRL_TT_LOAD_FLOOR_FACT f' in sql:
            self.rows = self.floor
        elif 'from RRL_TT_LOAD_THERMAL_FACT' in sql:
            self.rows = self.thermal
        else:
            self.rows = []

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def __iter__(self):
        return iter(self.rows)


def trip_cursor(monkeypatch, count, history):
    monkeypatch.setattr(status_module, 'authorized_trip_header', lambda *_: (7, 'V', 'D', 'P', 1))
    monkeypatch.setattr(status_module, 'loading_floor_read', lambda *args: {})
    monkeypatch.setattr(status_module, 'loading_thermal_read', lambda *args: {})
    members = [(i, str(i), 'P'+str(i), 2, 'A', 'L'+str(i), 'P'+str(i), 'LOADED', 'V', 'D', 1, 7, 'APPLIED') for i in range(count)]
    loads = [('L'+str(i), 'P'+str(i), 'V', 'D', 'LOADED' if i<count else 'UNLOADED', '10', 'a', None, None, None, 1, None, 1, 'P'+str(i), 'BOX', 'C', None, None) for i in range(history)]
    return Cursor(members, loads)


def test_660_cartons_and_prior_unloads_remain_visible(monkeypatch):
    cur = trip_cursor(monkeypatch, 660, 1980)
    result = status_module.read_loading_status(cur, 7, 'a')
    assert len(result['members']) == 660
    assert len(result['physical_places']) == 1980
    assert result['loaded_place_count'] == 660
    assert result['all_members_physically_loaded']
    assert not result['pending_st_ids']


@pytest.mark.parametrize('members,history,code', [(1001, 0, 'TRIP_MEMBER_BOUND_1000'), (1, 4001, 'TRIP_LOAD_HISTORY_BOUND_4000')])
def test_oversized_read_refuses_instead_of_showing_partial_trip(monkeypatch, members, history, code):
    with pytest.raises(TransportLoadingError) as error:
        status_module.read_loading_status(trip_cursor(monkeypatch, members, history), 7, 'a')
    assert error.value.code == code


@pytest.mark.parametrize('reader', [loading_floor_read, loading_thermal_read])
def test_confirmations_use_authorized_trip_without_oracle_in_limit(reader):
    cur = Cursor(floor=[('L659', 1, 'BOX', 'Box', 1, 'MANUAL', 'ref', None)], thermal=[('L659', '{}', None)])
    result = reader(cur, 7) if reader is loading_floor_read else reader(cur, 'V', 7)
    assert 'L659' in result['load_confirmations']
    queries = [(sql, binds) for sql, binds in cur.calls if 'join RRL_TT_HU_LOAD_FACT l' in sql]
    assert len(queries) == 1
    assert queries[0][1] == {'trip':7}


def test_capacity_counts_660_cartons_once_and_refuses_1001():
    package = dict(article='A', units_per_box=10, weight=Decimal(10), volume=Decimal('0.1'), boxes=Decimal(660), recipient_id='C')
    fact = ('L', 'LOADED', 'V', 10, Decimal('0.1'), json.dumps({'nodes':[dict(kind='STOCK',article='A',base_uom='EA',quantity='10')]}))
    class CapacityCursor(Cursor):
        def execute(self, sql, **binds):
            self.rows = [(7, 'V')] if 'RRL_TRADE_TRIP_LINK' in sql else self.loads
    trip = dict(vehicle_id='V')
    result = _loaded(CapacityCursor(loads=[fact]*660), 1, 'T', trip, [package])
    assert result['loaded_units'] == {'A':'6600'}
    assert result['places'] == 660
    assert result['overhead_kg'] == result['overhead_m3'] == 0
    with pytest.raises(TradeTransportError) as error:
        _loaded(CapacityCursor(loads=[fact]*1001), 1, 'T', trip, [package])
    assert error.value.code == 'TOPUP_AFTER_LOAD_FACT_BOUND_1000'
