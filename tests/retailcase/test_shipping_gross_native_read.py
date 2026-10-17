"""Native read port doubles prove wire/UOW only, not installed Oracle or HU acceptance."""
from contextlib import contextmanager
import hashlib
import json
import pytest
from api.wms_api_server.app.modules.quality.contracts_shipping_gross import ShippingGrossReadInput,parse_shipping_gross_read
from api.wms_api_server.app.modules.quality.infrastructure.shipping_gross_read import ShippingGrossNativeRead
from api.wms_api_server.app.modules.quality.domain.models import HuMassError


def envelope():
    p=dict(signature_domain='SHIPPING_GROSS',signature_version=1,root_uid='internal.outer',root_version=4,
           warehouse_id=13583852,cell='SHIP',nodes=[dict(uid='internal.outer',kind='CONTAINER',version=4,sscc='000001'),dict(uid='leaf',kind='STOCK',version=0)],
           links=[dict(parent='internal.outer',child='leaf')],shipments=[dict(document_id=1,rows_signature='A'*64,legs=[])],compiler_references=[],consolidation_expectations=None)
    wire=json.dumps(p,ensure_ascii=True,sort_keys=True,separators=(',',':'))
    return dict(signature_domain='SHIPPING_GROSS',signature_version=1,composition_signature=hashlib.sha256(wire.encode()).hexdigest().upper(),
                projection_json=wire,producer='RRL_SHIPPING_GROSS_READ.freeze',frozen_at='2026-10-15T18:00:00+00:00',expires_at='2026-10-15T18:02:00+00:00',
                quality_release_approved=False,stock_posted=False,capture_archived=False)


def request():return ShippingGrossReadInput('internal.outer','000001',4)


def with_expectations(value,*,missing=False):
    data=envelope();projection=json.loads(data['projection_json'])
    if missing:projection.pop('consolidation_expectations')
    else:projection['consolidation_expectations']=value
    data['projection_json']=json.dumps(projection,sort_keys=True,separators=(',',':'))
    data['composition_signature']=hashlib.sha256(data['projection_json'].encode()).hexdigest().upper()
    return json.dumps(data)


def token():
    return dict(domain='CONSOLIDATION_EXPECTATIONS',version=1,plan_id='future.internal.plan',plan_version=2,signature='A'*64)


def test_changed_expectations_invalidate_freeze_with_unchanged_physical_root():
    first=parse_shipping_gross_read(with_expectations(token()),request())
    revised=token();revised.update(plan_version=3,signature='B'*64)
    second=parse_shipping_gross_read(with_expectations(revised),request())
    assert first.composition.identifier==second.composition.identifier
    assert first.composition.content_version==second.composition.content_version
    assert first.composition.composition_signature!=second.composition.composition_signature
    assert second.consolidation_expectations.plan_version==3
    assert second.consolidation_expectations.signature=='B'*64
    assert second.quality_release_approved is False
    assert parse_shipping_gross_read(with_expectations(None),request()).consolidation_expectations is None


@pytest.mark.parametrize('change',['missing','shape','domain','version','plan','bytes','plan_version','zero','signature','extra'])
def test_malformed_expected_composition_is_not_a_legacy_unconfigured_root(change):
    value=token()
    if change=='shape':value=[]
    if change=='domain':value['domain']='ASM_FINAL'
    if change=='version':value['version']=True
    if change=='plan':value['plan_id']=' padded '
    if change=='bytes':value['plan_id']='\u044f'*51
    if change=='plan_version':value['plan_version']=True
    if change=='zero':value['plan_version']=0
    if change=='signature':value['signature']='not-a-native-signature'
    if change=='extra':value['ready']=True
    with pytest.raises(HuMassError,match='NATIVE_READ_REJECTED'):
        parse_shipping_gross_read(with_expectations(value,missing=change=='missing'),request())


def test_mass_free_generic_scan_and_digest():
    body=request().canonical_json();assert set(json.loads(body))=={'handling_unit_identifier','scan_container','expected_root_version'}
    result=parse_shipping_gross_read(json.dumps(envelope()),request())
    assert result.composition.identifier=='internal.outer'and result.quality_release_approved is False
    with pytest.raises(TypeError):ShippingGrossReadInput('internal.outer','000001',4,gross_kg='100')
    with pytest.raises(HuMassError):ShippingGrossReadInput('internal.outer','000001',True)


@pytest.mark.parametrize('change',['hash','domain','version','producer','quality','stock','capture','extra','expiry','root','scan','wire_duplicate'])
def test_wrong_native_envelope_is_rejected(change):
    data=envelope();r=request()
    if change=='hash':data['composition_signature']='F'*64
    if change=='domain':data['signature_domain']='ASM_FINAL'
    if change=='version':data['signature_version']=True
    if change=='producer':data['producer']='caller supplied'
    if change in ('quality','stock','capture'):data[{'quality':'quality_release_approved','stock':'stock_posted','capture':'capture_archived'}[change]]=True
    if change=='extra':data['gross_weight_kg']='100'
    if change=='expiry':data['expires_at']='2026-10-15T18:02:01+00:00'
    if change=='root':r=ShippingGrossReadInput('internal.outer','000001',5)
    if change=='scan':r=ShippingGrossReadInput('another','000001',4)
    if change=='wire_duplicate':
        data['projection_json']=data['projection_json'].replace('"root_version":4','"root_version":4,"root_version":4')
        data['composition_signature']=hashlib.sha256(data['projection_json'].encode()).hexdigest().upper()
    with pytest.raises(HuMassError,match='NATIVE_READ_REJECTED'):parse_shipping_gross_read(json.dumps(data),r)


@pytest.mark.parametrize('dirty',[False,True])
def test_readonly_is_first_statement_and_all_outcomes_rollback(dirty):
    calls=[]
    class Var:
        value=None
        def setvalue(self,index,value):self.value=value
        def getvalue(self):return self.value
    class Cursor:
        def execute(self,sql):
            calls.append(sql)
        def callfunc(self,name,result,args):
            calls.append(name)
            return '1.2.3'if dirty else None
        def var(self,_):return Var()
        def callproc(self,name,args):calls.append(name);args[-1].value=json.dumps(envelope())
        def close(self):calls.append('close')
    class Connection:
        def cursor(self):return Cursor()
        def rollback(self):calls.append('rollback')
        def commit(self):raise AssertionError('No commit allowed')
    @contextmanager
    def factory():yield Connection()
    port=ShippingGrossNativeRead(factory)
    if dirty:
        with pytest.raises(HuMassError,match='CLEAN_CONNECTION_REQUIRED'):port.freeze(request(),'actor')
        assert 'RRL_SHIPPING_GROSS_READ.freeze'not in calls
        assert 'rollback'not in calls and 'set transaction read only'not in calls
    else:
        assert port.freeze(request(),'actor').composition.signature_domain=='SHIPPING_GROSS'
        assert calls[1]=='set transaction read only'and calls[-2:]==['rollback','close']
    assert calls[0]=='DBMS_TRANSACTION.LOCAL_TRANSACTION_ID'
