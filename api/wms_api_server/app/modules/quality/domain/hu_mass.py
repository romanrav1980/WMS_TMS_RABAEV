"""Read-only mass projection of an existing native HU closure. No QC or stock effect."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
from typing import Any
from .models import (CompositionIdentity,FrozenHuMassInput,HuMassError,HuMassNode,
                     HuMassProjection,MassEvidence,NodeMassProjection,aware,utc_instant)


@dataclass(frozen=True)
class _Contribution:
    value: Decimal | None
    estimated: bool
    reason: str


def _closure(source: FrozenHuMassInput) -> dict[str,HuMassNode]:
    nodes={node.binding.identifier:node for node in source.nodes}
    if len(nodes)!=len(source.nodes)or source.root.identifier not in nodes:
        raise HuMassError('HU_MASS_DUPLICATE_OR_MISSING_ROOT')
    root=nodes[source.root.identifier]
    if root.binding!=source.root:raise HuMassError('HU_MASS_ROOT_FREEZE_CONFLICT')
    parents:dict[str,int]={};leaf_keys:set[str]=set()
    for node in nodes.values():
        if(node.warehouse_id,node.cell)!=(root.warehouse_id,root.cell):
            raise HuMassError('HU_MASS_PHYSICAL_CLOSURE_NOT_COLOCATED')
        for child in node.direct_children:
            if child not in nodes:raise HuMassError('HU_MASS_CHILD_MISSING')
            parents[child]=parents.get(child,0)+1
            if parents[child]!=1:raise HuMassError('HU_MASS_MULTIPLE_PARENT_OR_DUPLICATE_CHILD')
        for key in node.leaf_stock_keys:
            if key in leaf_keys:raise HuMassError('HU_MASS_LEAF_STOCK_REPEATED')
            leaf_keys.add(key)
            if len(leaf_keys)>10000:raise HuMassError('HU_MASS_LEAF_KEY_BOUND_10000')
    seen:set[str]=set()
    def visit(uid:str,depth:int) -> None:
        if depth>16:raise HuMassError('HU_MASS_DEPTH_BOUND_16')
        if uid in seen:raise HuMassError('HU_MASS_CYCLE_OR_REPEATED_NODE')
        seen.add(uid)
        for child in nodes[uid].direct_children:visit(child,depth+1)
    visit(source.root.identifier,0)
    if len(seen)!=len(nodes)or source.root.identifier in parents:
        raise HuMassError('HU_MASS_DISCONNECTED_OR_CYCLIC_CLOSURE')
    return nodes


def _state(evidence:MassEvidence|None,node:HuMassNode,basis:str,as_of:datetime) -> str:
    if evidence is None:return 'MISSING'
    if evidence.binding!=node.binding:return 'STALE_COMPOSITION'
    if evidence.basis!=basis:return 'BASIS_MISMATCH'
    if utc_instant(evidence.effective_at)>utc_instant(as_of):return 'FUTURE'
    if utc_instant(evidence.expires_at)<=utc_instant(as_of):return 'EXPIRED'
    return 'VALID_AT_AS_OF'


def _freeze(source:FrozenHuMassInput,current:CompositionIdentity,as_of:datetime) -> str:
    if current!=source.root:return 'STALE'
    if utc_instant(as_of)<utc_instant(source.frozen_at):return 'FUTURE'
    if utc_instant(as_of)>=utc_instant(source.expires_at):return 'EXPIRED'
    return 'CURRENT'


def _observed(node:HuMassNode,as_of:datetime,root:bool,frozen_at:datetime) -> str:
    state=_state(node.observed_gross,node,'GROSS',as_of)
    if state!='VALID_AT_AS_OF':return state
    assert node.observed_gross is not None
    if root and(node.observed_gross.source_domain!='SHIPPING_GROSS'or node.observed_gross.source_version!=1):
        return 'SHIPPING_DOMAIN_MISMATCH'
    if root and utc_instant(node.observed_gross.effective_at)<utc_instant(frozen_at):return 'BEFORE_FREEZE'
    return state


def _expected(node:HuMassNode,children:dict[str,_Contribution],as_of:datetime) -> tuple[_Contribution,str,tuple[str,...]]:
    if not node.direct_children:
        state=_state(node.estimated_gross,node,'GROSS',as_of)
        if state=='VALID_AT_AS_OF':
            assert node.estimated_gross is not None
            return _Contribution(node.estimated_gross.weight_kg,True,'ESTIMATED'),'ESTIMATED',()
        return _Contribution(None,False,'UNKNOWN'),'UNKNOWN',('NO_LEAF_EXPECTATION:'+state,)
    problems=[uid+':'+children[uid].reason for uid in node.direct_children if children[uid].value is None]
    tare_state=_state(node.own_tare,node,'TARE',as_of)
    if tare_state!='VALID_AT_AS_OF':problems.append('OWN_TARE:'+tare_state)
    if problems:return _Contribution(None,False,'UNKNOWN'),'UNKNOWN',tuple(sorted(problems))
    assert node.own_tare is not None
    with localcontext()as context:
        context.prec=64
        total=node.own_tare.weight_kg+sum((children[uid].value for uid in node.direct_children),Decimal(0))
    estimated=node.own_tare.source=='ESTIMATED'or any(children[uid].estimated for uid in node.direct_children)
    kind='CALCULATED_WITH_ESTIMATES'if estimated else'CALCULATED_MEASURED_INPUTS'
    return _Contribution(total,estimated,kind),kind,()


def _json_value(value:Any) -> str:
    if isinstance(value,Decimal):
        text=format(value,'f')
        return text.rstrip('0').rstrip('.')if '.'in text else text
    if isinstance(value,datetime):return value.astimezone(timezone.utc).isoformat()
    raise TypeError(type(value).__name__)


def _fingerprint(source:FrozenHuMassInput,current:CompositionIdentity,results:list[NodeMassProjection],freeze:str) -> str:
    payload=asdict(source)
    payload['nodes']=sorted(payload['nodes'],key=lambda node:node['binding']['identifier'])
    for node in payload['nodes']:
        node['direct_children']=sorted(node['direct_children']);node['leaf_stock_keys']=sorted(node['leaf_stock_keys'])
    value=dict(domain='HU_MASS_PROJECTION',version=1,input=payload,current=asdict(current),freeze_state=freeze,
               results=[asdict(result)for result in results])
    body=json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':'),default=_json_value).encode()
    return hashlib.sha256(body).hexdigest().upper()


def project_hu_mass(source:FrozenHuMassInput,current:CompositionIdentity,as_of:datetime) -> HuMassProjection:
    """No tolerance, stable classifier, native authority verification or release decision here."""
    if not isinstance(source,FrozenHuMassInput)or not isinstance(current,CompositionIdentity):
        raise HuMassError('HU_MASS_TYPED_NATIVE_INPUT_REQUIRED')
    aware(as_of)
    nodes=_closure(source);freeze=_freeze(source,current,as_of)
    results:dict[str,NodeMassProjection]={};contributions:dict[str,_Contribution]={}
    def compute(uid:str) -> None:
        node=nodes[uid]
        for child in node.direct_children:compute(child)
        observed=_observed(node,as_of,uid==source.root.identifier,source.frozen_at)
        expected,kind,reasons=_expected(node,contributions,as_of)
        if freeze!='CURRENT':
            expected=_Contribution(None,False,'FROZEN_'+freeze);kind='UNKNOWN';reasons=('FROZEN_'+freeze,)
        difference=None
        if freeze=='CURRENT'and observed=='VALID_AT_AS_OF'and expected.value is not None:
            assert node.observed_gross is not None
            with localcontext()as context:
                context.prec=64;difference=node.observed_gross.weight_kg-expected.value
        results[uid]=NodeMassProjection(uid,expected.value,kind,node.observed_gross,observed,difference,reasons)
        if freeze=='CURRENT'and observed=='VALID_AT_AS_OF':
            assert node.observed_gross is not None
            contributions[uid]=_Contribution(node.observed_gross.weight_kg,False,'MEASURED')
        else:contributions[uid]=expected
    compute(source.root.identifier)
    ordered=[results[uid]for uid in sorted(results)]
    return HuMassProjection(source.root.identifier,freeze,as_of,tuple(ordered),_fingerprint(source,current,ordered,freeze))
