"""Pure counterexamples for projected mass; no native/HW/QC approval claim."""
from dataclasses import FrozenInstanceError,replace
from datetime import datetime,timedelta,timezone
from decimal import Decimal,localcontext
import hashlib
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'api/wms_api_server'))
import pytest
from app.modules.quality.public import (CompositionIdentity,FrozenHuMassInput,HuMassError,HuMassNode,MassEvidence,project_hu_mass)
NOW=datetime(2030,1,1,tzinfo=timezone.utc)


def binding(uid,version=1):
    return CompositionIdentity(uid,version,'NATIVE_HU_CLOSURE',1,hashlib.sha256((uid+str(version)).encode()).hexdigest().upper())


def evidence(uid,kg,basis='GROSS',source='MEASURED',domain='CHILD_ARCHIVE',**changes):
    return MassEvidence(**dict(binding=binding(uid),basis=basis,unit='KG',weight_kg=Decimal(kg),source=source,source_domain=domain,
        source_version=1,reference='ARCHIVE:'+uid+':'+basis,producer_proof='NATIVE_READ:'+uid,effective_at=NOW,expires_at=NOW+timedelta(minutes=10),**changes))


def node(uid,children=(),tare=None,observed=None,estimate=None,**changes):
    return HuMassNode(binding(uid),7,'SHIP-CELL',children,()if children else('STOCK:'+uid,),tare,observed,estimate,**changes)


def frozen(*nodes):
    return FrozenHuMassInput(nodes[0].binding,nodes,'NATIVE_HU_READ:SNAPSHOT',NOW,NOW+timedelta(minutes=20))


def projected(source,at=NOW):
    result=project_hu_mass(source,source.root,at)
    return result,{row.identifier:row for row in result.nodes}


def test_direct_child_actual_is_added_once_not_all_descendants_or_double_tare():
    leaf=node('leaf',observed=evidence('leaf','10'))
    box=node('box',('leaf',),evidence('box','2','TARE'),evidence('box','12'))
    top=node('internal:TOP',('box',),evidence('internal:TOP','1','TARE'),evidence('internal:TOP','13',domain='SHIPPING_GROSS'))
    result,rows=projected(frozen(top,box,leaf))
    assert rows['box'].expected_gross_kg==12
    assert rows['internal:TOP'].expected_gross_kg==13 and rows['internal:TOP'].difference_kg==0
    assert rows['internal:TOP'].expected_source=='CALCULATED_MEASURED_INPUTS'
    assert result.quality_release_approved is False and result.producer_proof_verified is False


def test_unknown_child_keeps_independent_measured_outer_immutable():
    actual=evidence('top','15',domain='SHIPPING_GROSS')
    source=frozen(node('top',('unknown',),evidence('top','1','TARE'),actual),node('unknown'))
    _,rows=projected(source)
    assert rows['top'].expected_gross_kg is None and rows['top'].difference_kg is None
    assert rows['top'].observed_gross is actual and rows['top'].observed_state=='VALID_AT_AS_OF'
    assert rows['top'].expected_source=='UNKNOWN'and rows['top'].reasons
    with pytest.raises(FrozenInstanceError):actual.weight_kg=Decimal('1')


def test_child_outer_measurement_remains_usable_when_its_expected_is_unknown():
    unknown=node('unknown')
    box=node('box',('unknown',),None,evidence('box','9'))
    top=node('top',('box',),evidence('top','1','TARE'))
    _,rows=projected(frozen(top,box,unknown))
    assert rows['box'].expected_source=='UNKNOWN'
    assert rows['top'].expected_gross_kg==10


def test_explicit_estimate_is_never_promoted_to_measurement():
    source=frozen(node('top',('leaf',),evidence('top','1','TARE')),node('leaf',estimate=evidence('leaf','8',source='ESTIMATED',domain='SKU_POLICY')))
    _,rows=projected(source)
    assert rows['top'].expected_gross_kg==9 and rows['top'].expected_source=='CALCULATED_WITH_ESTIMATES'
    assert rows['leaf'].expected_source=='ESTIMATED'and rows['leaf'].observed_gross is None


def test_missing_own_tare_is_unknown_not_implicit_zero():
    _,rows=projected(frozen(node('top',('leaf',)),node('leaf',observed=evidence('leaf','8'))))
    assert rows['top'].expected_gross_kg is None and 'OWN_TARE:MISSING'in rows['top'].reasons


@pytest.mark.parametrize('change,state',[
    (dict(binding=binding('leaf',2)),'STALE_COMPOSITION'),
    (dict(expires_at=NOW+timedelta(seconds=1)),'EXPIRED'),
    (dict(effective_at=NOW+timedelta(seconds=10)),'FUTURE'),
    (dict(basis='TARE'),'BASIS_MISMATCH')])
def test_bad_child_evidence_cannot_make_parent_total(change,state):
    bad=replace(evidence('leaf','8'),**change)
    source=frozen(node('top',('leaf',),evidence('top','1','TARE')),node('leaf',observed=bad))
    _,rows=projected(source,NOW+timedelta(seconds=2))
    assert rows['leaf'].observed_state==state and rows['top'].expected_gross_kg is None
    assert rows['leaf'].observed_gross is bad


@pytest.mark.parametrize('domain,version',[('ASM_FINAL',3),('SMALL_HU',3),('SHIPPING_GROSS',2)])
def test_root_asm_and_legacy_v3_are_not_shipping_gross(domain,version):
    actual=replace(evidence('top','9',domain=domain),source_version=version)
    source=frozen(node('top',('leaf',),evidence('top','1','TARE'),actual),node('leaf',observed=evidence('leaf','8')))
    _,rows=projected(source)
    assert rows['top'].observed_state=='SHIPPING_DOMAIN_MISMATCH'and rows['top'].difference_kg is None
    assert rows['top'].observed_gross is actual


@pytest.mark.parametrize('at,state',[(NOW-timedelta(seconds=1),'FUTURE'),(NOW+timedelta(minutes=20),'EXPIRED')])
def test_freeze_window_is_not_refreshed_by_reading_again(at,state):
    source=frozen(node('top',('leaf',),evidence('top','1','TARE'),evidence('top','9',domain='SHIPPING_GROSS')),node('leaf',observed=evidence('leaf','8')))
    result,rows=projected(source,at)
    assert result.freeze_state==state and rows['top'].expected_gross_kg is None and rows['top'].difference_kg is None


def test_changed_current_native_signature_invalidates_calculation_without_rewriting_observation():
    source=frozen(node('top',observed=evidence('top','9',domain='SHIPPING_GROSS')))
    result=project_hu_mass(source,replace(source.root,composition_signature='F'*64),NOW)
    assert result.freeze_state=='STALE'and result.nodes[0].observed_gross==source.nodes[0].observed_gross


def test_native_before_freeze_measurement_is_historical_not_rebound():
    actual=replace(evidence('top','9',domain='SHIPPING_GROSS'),effective_at=NOW-timedelta(seconds=1))
    _,rows=projected(frozen(node('top',observed=actual)))
    assert rows['top'].observed_state=='BEFORE_FREEZE'


@pytest.mark.parametrize('nodes,marker',[
    ((node('top',('top',)),),'CYCLE'),
    ((node('top',('a','a')),node('a')),'DUPLICATE_CHILD'),
    ((node('top',('a','b')),node('a',('leaf',)),node('b',('leaf',)),node('leaf')),'MULTIPLE_PARENT'),
    ((node('top',('missing',)),),'CHILD_MISSING'),
    ((node('top'),node('stray')),'DISCONNECTED'),
    ((node('top',('leaf',)),replace(node('leaf'),cell='NOT_PHYSICALLY_ARRIVED')),'NOT_COLOCATED'),
    ((node('top',('a','b')),node('a'),replace(node('b'),leaf_stock_keys=('STOCK:a',))),'LEAF_STOCK_REPEATED')])
def test_invalid_native_projection_shapes_fail_closed(nodes,marker):
    with pytest.raises(HuMassError,match=marker):projected(frozen(*nodes))


def test_depth_and_node_bounds_are_enforced():
    chain=tuple(node(str(i),(str(i+1),))for i in range(17))+(node('17'),)
    with pytest.raises(HuMassError,match='DEPTH_BOUND'):projected(frozen(*chain))
    with pytest.raises(HuMassError,match='CLOSURE_BOUND'):frozen(*(node(str(i))for i in range(201)))


def test_exact_decimal_arithmetic_is_independent_of_process_context_and_input_order():
    a=node('a',observed=evidence('a','123456789.123456789'))
    b=node('b',observed=evidence('b','0.000000001'))
    top=node('top',('a','b'),evidence('top','0','TARE'))
    source=frozen(top,a,b)
    with localcontext()as context:
        context.prec=6
        result,rows=projected(source)
    assert rows['top'].expected_gross_kg==Decimal('123456789.123456790')
    reordered=replace(source,nodes=(replace(top,direct_children=('b','a')),b,a))
    assert projected(reordered)[0].projection_sha256==result.projection_sha256


@pytest.mark.parametrize('value',[float('nan'),Decimal('NaN'),Decimal('Infinity'),Decimal('-1'),Decimal('0.0000000001')])
def test_invalid_mass_never_becomes_a_fact(value):
    with pytest.raises(HuMassError):replace(evidence('leaf','1'),weight_kg=value)


def test_units_basis_source_and_timezone_are_explicit():
    with pytest.raises(HuMassError):replace(evidence('leaf','1'),unit='LB')
    with pytest.raises(HuMassError):replace(evidence('leaf','1'),producer_proof='')
    with pytest.raises(HuMassError):replace(evidence('leaf','1'),effective_at=NOW.replace(tzinfo=None))
    with pytest.raises(HuMassError):node('leaf',observed=evidence('leaf','1',source='ESTIMATED'))

def test_projection_cannot_be_constructed_as_verified_or_approved():
    result,_=projected(frozen(node('top')))
    with pytest.raises((ValueError,TypeError)):replace(result,quality_release_approved=True)
    with pytest.raises((ValueError,TypeError)):replace(result,producer_proof_verified=True)


def test_dst_fold_windows_and_evidence_use_instants_not_equal_zone_walltime():
    from zoneinfo import ZoneInfo
    zone=ZoneInfo('Europe/Berlin')
    first=datetime(2026,10,25,2,30,tzinfo=zone,fold=0)
    last=datetime(2026,10,25,2,45,tzinfo=zone,fold=1)
    def fact(uid,kg,basis='GROSS',domain='CHILD_ARCHIVE'):
        return replace(evidence(uid,kg,basis,domain=domain),effective_at=first,expires_at=last)
    top=node('top',('leaf',),fact('top','1','TARE'),fact('top','9',domain='SHIPPING_GROSS'))
    leaf=node('leaf',observed=fact('leaf','8'))
    source=FrozenHuMassInput(top.binding,(top,leaf),'NATIVE:UTC',first,last)
    for as_of in [datetime(2026,10,25,2,50,tzinfo=zone,fold=0),datetime(2026,10,25,2,15,tzinfo=zone,fold=1)]:
        result=project_hu_mass(source,source.root,as_of)
        root=next(row for row in result.nodes if row.identifier=='top')
        assert result.freeze_state=='CURRENT'and root.observed_state=='VALID_AT_AS_OF'and root.difference_kg==0
    # Same local hour/minute across the fold is a genuine positive one-hour window.
    replace(fact('leaf','8'),expires_at=datetime(2026,10,25,2,30,tzinfo=zone,fold=1))
    replace(source,expires_at=datetime(2026,10,25,2,30,tzinfo=zone,fold=1))


def test_dst_before_freeze_uses_utc_and_does_not_rebind_old_measurement():
    from zoneinfo import ZoneInfo
    zone=ZoneInfo('Europe/Berlin')
    old=datetime(2026,10,25,2,40,tzinfo=zone,fold=0)
    start=datetime(2026,10,25,2,10,tzinfo=zone,fold=1)
    end=datetime(2026,10,25,3,10,tzinfo=zone)
    actual=replace(evidence('top','9',domain='SHIPPING_GROSS'),effective_at=old,expires_at=end)
    top=node('top',observed=actual)
    source=FrozenHuMassInput(top.binding,(top,),'NATIVE:UTC',start,end)
    assert project_hu_mass(source,source.root,start).nodes[0].observed_state=='BEFORE_FREEZE'


def test_nonexistent_local_time_is_not_accepted_as_an_aware_fact():
    from zoneinfo import ZoneInfo
    imaginary=datetime(2026,3,29,2,30,tzinfo=ZoneInfo('Europe/Berlin'))
    with pytest.raises(HuMassError,match='NONEXISTENT'):
        replace(evidence('leaf','1'),effective_at=imaginary)


@pytest.mark.parametrize('changes',[{'direct_children':('x',)*201},{'leaf_stock_keys':('x',)*10001}])
def test_individual_projection_collections_are_bounded_before_walk(changes):
    with pytest.raises(HuMassError,match='COLLECTION_BOUND'):replace(node('leaf'),**changes)
