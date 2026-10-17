"""Scope is checked in the physical owner's warehouse before tree/QC disclosure."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'api/wms_api_server'))
import pytest
from fastapi import HTTPException
from app.modules.inventory.infrastructure.hu_view_access import assert_hu_view, assert_resolved_hu_view
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu


class Cursor:
    def __init__(self, allowed=1):self.allowed=allowed;self.calls=[]
    def execute(self,sql,**params):self.calls.append((sql,params))
    def fetchone(self):return(self.allowed,)


@pytest.mark.parametrize('allowed',[0,None,2])
def test_current_native_denial_stays_denial(allowed):
    with pytest.raises(HTTPException)as error:assert_hu_view(Cursor(allowed),'viewer',42)
    assert error.value.status_code==403


def test_native_scope_receives_actual_warehouse_not_home_warehouse():
    cur=Cursor()
    assert_hu_view(cur,'viewer',5062399)
    sql,params=cur.calls[0]
    assert 'RRL_ACCESS_API.allowed'in sql
    assert params=={'p_actor':'viewer','p_warehouse':'5062399'}


@pytest.mark.parametrize('warehouses',[[],[{'ware_id':None}],[{'ware_id':0}],[{'ware_id':1},{'ware_id':2},{'ware_id':3}]])
def test_unknown_or_unbounded_physical_location_is_not_allowed(warehouses):
    class Gateway:
        cursor=Cursor()
        def fetch_all(self,*args):return warehouses
    with pytest.raises(HTTPException)as error:
        assert_resolved_hu_view(Gateway(),{'uid_pallet':'stock'},'viewer')
    assert error.value.status_code==403


@pytest.mark.parametrize('resolved',[
    {'case_task_id':1131},
    {'uid_pallet':'stock'},
    {'uid_pallet':'hu','hu_shipped_operation':'SHIP:1'},
])
def test_case_current_stock_and_departure_use_native_warehouse_authority(resolved):
    class Gateway:
        cursor=Cursor()
        def __init__(self):self.queries=[]
        def fetch_all(self,sql,params):self.queries.append(sql);return[{'ware_id':5062399}]
    g=Gateway();assert_resolved_hu_view(g,resolved,'viewer')
    assert g.cursor.calls[-1][1]['p_warehouse']=='5062399'
    if resolved.get('hu_shipped_operation'):
        assert 'composition_at_departure.warehouse'in g.queries[0]


def test_denied_identity_never_reads_composition_or_archive_body():
    class Gateway:
        cursor=Cursor(0)
        def __init__(self):self.calls=[]
        def fetch_all(self,sql,params):
            self.calls.append(sql)
            if len(self.calls)==1:return[{'uid_pallet':'HU:1','case_task_id':None,'hu_shipped_operation':None}]
            if len(self.calls)==2:return[{'ware_id':42}]
            pytest.fail('Composition was read before current scope admission')
    g=Gateway()
    with pytest.raises(HTTPException)as error:WarehouseHu(g)._preview('HU:1','viewer')
    assert error.value.status_code==403 and len(g.calls)==2


def test_ambiguous_scan_never_chooses_first_identity():
    class Gateway:
        def fetch_all(self,*args):return[{'uid_pallet':'a'},{'uid_pallet':'b'}]
    with pytest.raises(HTTPException)as error:WarehouseHu(Gateway())._preview('duplicate','viewer')
    assert error.value.status_code==409
